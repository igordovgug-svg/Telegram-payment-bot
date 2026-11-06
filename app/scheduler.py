import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.db.models import Subscription, User
from app.db.session import async_session
from app.services.access import revoke_access

log = logging.getLogger(__name__)

REMIND_BEFORE = timedelta(days=3)


async def send_reminders(bot: Bot) -> None:
    now = datetime.now(timezone.utc)
    async with async_session() as session:
        rows = await session.execute(
            select(Subscription, User)
            .join(User, User.id == Subscription.user_id)
            .where(
                Subscription.is_active,
                Subscription.expires_at.is_not(None),
                Subscription.expires_at > now,
                Subscription.expires_at <= now + REMIND_BEFORE,
                Subscription.reminder_sent.is_(False),
            )
        )
        for sub, user in rows.all():
            try:
                await bot.send_message(
                    user.telegram_id,
                    f"Підписка закінчується {sub.expires_at:%d.%m.%Y}. "
                    "Щоб продовжити, натисніть /start і оберіть тариф.",
                )
            except Exception:
                log.exception("Не вдалося надіслати нагадування user=%s", user.id)
            sub.reminder_sent = True  # навіть при помилці, щоб не повторювати вічно
        await session.commit()


async def expire_subscriptions(bot: Bot) -> None:
    now = datetime.now(timezone.utc)
    async with async_session() as session:
        rows = await session.execute(
            select(Subscription, User)
            .join(User, User.id == Subscription.user_id)
            .where(
                Subscription.is_active,
                Subscription.expires_at.is_not(None),
                Subscription.expires_at <= now,
            )
        )
        for sub, user in rows.all():
            try:
                removed = await revoke_access(bot, user.telegram_id)  
            except Exception:
                # підписку лишаємо активною: наступний запуск спробує ще раз
                log.exception("Не вдалося видалити з каналу user=%s", user.id)
                continue
            if not removed:                                                # додано
                log.warning(
                    "user=%s адмін/власник каналу, видалити неможливо, "
                    "підписку лише деактивовано", user.id,
                )
            sub.is_active = False
            await session.commit()
            try:
                await bot.send_message(
                    user.telegram_id,
                    "Підписка закінчилась, доступ до каналу закрито. "
                    "Щоб повернутися, натисніть /start.",
                )
            except Exception:
                log.exception("Не вдалося повідомити про завершення user=%s", user.id)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    first_run = datetime.now(timezone.utc)  # перший запуск одразу при старті
    for job in (send_reminders, expire_subscriptions):
        scheduler.add_job(
            job, "interval", minutes=30, args=[bot], next_run_time=first_run
        )
    return scheduler
from datetime import datetime, timezone

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import get_active_subscription, get_or_create_user
from app.services.access import create_invite_link

router = Router()


@router.message(Command("access"))
async def cmd_access(message: Message, session: AsyncSession, bot: Bot):
    user = await get_or_create_user(
        session, message.from_user.id, message.from_user.username
    )
    sub = await get_active_subscription(session, user.id)
    now = datetime.now(timezone.utc)

    if sub is None or (sub.expires_at is not None and sub.expires_at <= now):
        await message.answer("Активної підписки немає. Натисніть /start, щоб обрати тариф.")
        return

    link = await create_invite_link(bot)
    await message.answer(f"Ваше посилання в канал (одноразове, діє 24 год):\n{link}")
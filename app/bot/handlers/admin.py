from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, User
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import AdminFilter
from app.services.stats import get_active_subscribers, get_last_payments, get_stats

router = Router()
router.message.filter(AdminFilter())  
router.callback_query.filter(AdminFilter())  


def display_name(user: User) -> str:
    return f"@{user.username}" if user.username else f"id{user.telegram_id}"


@router.message(Command("stats"))
async def cmd_stats(message: Message, session: AsyncSession):
    s = await get_stats(session)
    await message.answer(
        "📊 Статистика\n"
        f"Користувачів: {s['users']}\n"
        f"Активних підписок: {s['active_subs']}\n"
        f"Оплачених замовлень: {s['paid_count']}\n"
        f"Дохід усього: {s['revenue']:.0f} грн\n"
        f"Дохід за 30 днів: {s['revenue_30']:.0f} грн\n"
        f"Очікують оплати (pending): {s['pending']}"
    )


@router.message(Command("payments"))
async def cmd_payments(message: Message, session: AsyncSession):
    rows = await get_last_payments(session)
    if not rows:
        await message.answer("Оплат ще немає.")
        return
    lines = [
        f"#{o.id} · {display_name(u)} · {t.title} · {o.amount:.0f} грн · "
        f"{o.paid_at:%d.%m %H:%M} UTC"
        for o, u, t in rows
    ]
    await message.answer("💳 Останні оплати:\n" + "\n".join(lines))


@router.message(Command("subscribers"))
async def cmd_subscribers(message: Message, session: AsyncSession):
    rows = await get_active_subscribers(session)
    if not rows:
        await message.answer("Активних підписників немає.")
        return
    lines = [
        f"{display_name(u)} · до "
        + (f"{s.expires_at:%d.%m.%Y}" if s.expires_at else "назавжди")
        for s, u in rows
    ]
    await message.answer("👥 Активні підписники:\n" + "\n".join(lines))
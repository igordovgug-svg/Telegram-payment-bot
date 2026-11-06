from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import pay_kb, tariffs_kb          # змінено
from app.db.repositories import (
    create_order,
    get_active_tariffs,
    get_or_create_user,
    get_tariff,
)
from app.services.liqpay import build_checkout_url        # додано

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    await get_or_create_user(
        session, message.from_user.id, message.from_user.username
    )
    tariffs = await get_active_tariffs(session)

    await message.answer(
        f"Вітаю, {message.from_user.first_name}! Оберіть тариф:",
        reply_markup=tariffs_kb(tariffs),
    )


@router.callback_query(F.data.startswith("tariff:"))
async def choose_tariff(callback: CallbackQuery, session: AsyncSession):
    tariff_id = int(callback.data.split(":")[1])

    tariff = await get_tariff(session, tariff_id)
    if tariff is None or not tariff.is_active:
        await callback.answer("Цей тариф недоступний", show_alert=True)
        return

    user = await get_or_create_user(
        session, callback.from_user.id, callback.from_user.username
    )
    order = await create_order(session, user, tariff)
    url = build_checkout_url(order, f"Python Club: {tariff.title}")   # додано

    await callback.message.answer(
        f"Замовлення #{order.id}\n"
        f"Тариф: {tariff.title}, до сплати: {order.amount:.0f} грн.",
        reply_markup=pay_kb(url),                                     # змінено
    )
    await callback.answer()
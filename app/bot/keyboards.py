from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup   # додано

from app.db.models import Tariff


def tariffs_kb(tariffs: list[Tariff]):
    kb = InlineKeyboardBuilder()
    for t in tariffs:
        kb.button(text=f"{t.title}: {t.price:.0f} грн", callback_data=f"tariff:{t.id}")
    kb.adjust(1)  # по одній кнопці в рядок
    return kb.as_markup()


def pay_kb(url: str) -> InlineKeyboardMarkup:                           # додано
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Оплатити", url=url)]]
    )
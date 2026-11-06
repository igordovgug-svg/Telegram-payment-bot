from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.services.admin import is_admin


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        return await is_admin(bot, message.from_user.id)
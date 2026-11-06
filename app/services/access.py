from datetime import datetime, timedelta, timezone

from aiogram import Bot
from aiogram.enums import ChatMemberStatus    
from app.config import settings


async def create_invite_link(bot: Bot) -> str:
    link = await bot.create_chat_invite_link(
        chat_id=settings.channel_id,
        member_limit=1,  # одне вступлення
        expire_date=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    return link.invite_link


async def revoke_access(bot: Bot, telegram_id: int) -> bool:    # змінено: повертає bool
    member = await bot.get_chat_member(settings.channel_id, telegram_id)   # додано

    # власника й адміністраторів видалити неможливо
    if member.status in (ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR):   # додано
        return False

    # людини вже немає в каналі, робити нічого                  # додано
    if member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
        return True

    await bot.ban_chat_member(settings.channel_id, telegram_id)
    await bot.unban_chat_member(
        settings.channel_id, telegram_id, only_if_is_banned=True
    )
    return True

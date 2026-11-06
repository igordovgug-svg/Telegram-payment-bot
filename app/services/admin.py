import logging    

from aiogram import Bot

from aiogram.enums import ChatMemberStatus

from app.config import settings

ADMIN_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.CREATOR,
    ChatMemberStatus.ADMINISTRATOR
}


log = logging.getLogger(__name__)  


async def is_admin(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(settings.admin_group_id, user_id)
    except Exception:
        log.exception("is_admin: не вдалося перевірити user=%s", user_id)   # змінено
        return False
    return member.status in ADMIN_STATUSES
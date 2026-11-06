import asyncio

from aiogram import Bot

from app.config import settings


async def check(bot: Bot, me_id: int, name: str, chat_id: int):
    print(f"--- {name} ({chat_id}) ---")
    try:
        chat = await bot.get_chat(chat_id)
        member = await bot.get_chat_member(chat_id, me_id)
    except Exception as e:
        print("помилка:", e)
        return
    print("назва:", chat.title, "| тип:", chat.type)
    print("статус бота:", member.status)
    print("can_invite_users:", getattr(member, "can_invite_users", None))
    print("can_restrict_members:", getattr(member, "can_restrict_members", None))


async def main():
    bot = Bot(settings.bot_token)
    me = await bot.get_me()
    await check(bot, me.id, "CHANNEL_ID", settings.channel_id)
    await check(bot, me.id, "ADMIN_GROUP_ID", settings.admin_group_id)
    await bot.session.close()


asyncio.run(main())
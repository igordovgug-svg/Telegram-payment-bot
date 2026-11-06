import asyncio
import sys

from aiogram import Bot

from app.config import settings


async def main():
    bot = Bot(settings.bot_token)
    try:
        m = await bot.get_chat_member(settings.admin_group_id, int(sys.argv[1]))
        print("status:", m.status)
    except Exception as e:
        print("ПОМИЛКА:", type(e).__name__, e)
    await bot.session.close()


asyncio.run(main())
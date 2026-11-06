import asyncio
import logging

import uvicorn
from aiogram import Bot, Dispatcher
from fastapi import FastAPI

from app.api import liqpay
from app.bot.handlers import access, admin, start                    # змінено
from app.bot.middlewares import DbSessionMiddleware
from app.config import settings
from app.db.session import async_session
from app.scheduler import setup_scheduler                     # додано


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.update.outer_middleware(DbSessionMiddleware(async_session))
    dp.include_router(start.router)
    dp.include_router(access.router)   
    dp.include_router(admin.router)                         # додано

    api = FastAPI()
    api.state.bot = bot
    api.include_router(liqpay.router)
    server = uvicorn.Server(
        uvicorn.Config(api, host=settings.api_host, port=settings.api_port, log_level="info")
    )

    scheduler = setup_scheduler(bot)                          # додано
    scheduler.start()                                         # додано

    await asyncio.gather(dp.start_polling(bot), server.serve())


if __name__ == "__main__":
    asyncio.run(main())
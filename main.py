import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import admin, moderation, settings, welcome, verification, utils, errors
from middlewares.rate_limit import RateLimitMiddleware  # optional

logging.basicConfig(level=logging.INFO)

async def main():
    # Initialize DB
    await init_db()

    # Bot and dispatcher
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Include routers
    dp.include_router(admin.router)
    dp.include_router(moderation.router)
    dp.include_router(settings.router)
    dp.include_router(welcome.router)
    dp.include_router(verification.router)
    dp.include_router(utils.router)
    dp.include_router(errors.router)

    # Middlewares (optional)
    # dp.message.middleware(RateLimitMiddleware())

    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
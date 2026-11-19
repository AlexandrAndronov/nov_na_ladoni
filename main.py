
import asyncio
import logging

from handlers.admin import router as admin_router
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from database.db import init_db

from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.quest import router as quest_router
from handlers.menu import router as menu_router

logging.basicConfig(level=logging.INFO)

session = AiohttpSession(
    proxy="http://127.0.0.1:12334"
)

bot = Bot(
    token=BOT_TOKEN,
    session=session
)

from aiogram.fsm.storage.memory import MemoryStorage

dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start_router)
dp.include_router(quest_router)
dp.include_router(menu_router)
dp.include_router(admin_router)

async def main():
    print("Инициализация базы данных...")
    await init_db()

    print("База данных готова!")
    print("Бот запускается...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_ID
from database.db import get_admin_stats


router = Router()


@router.message(Command("admin"))
async def admin_handler(message: Message):
    if message.from_user.id != int(ADMIN_ID):
        await message.answer("⛔ У тебя нет доступа к административной панели.")
        return

    stats = await get_admin_stats()

    await message.answer(
        "📊 АДМИНИСТРАТИВНАЯ СТАТИСТИКА\n\n"
        f"👥 Всего зарегистрировано: {stats['total_users']}\n"
        f"🚀 Начали прохождение: {stats['started_users']}\n"
        f"🏆 Завершили квест: {stats['completed_users']}\n\n"
        f"⭐ Всего набрано баллов: {stats['total_score']}\n"
        f"📝 Всего выполнено заданий: {stats['total_tasks']}"
    )

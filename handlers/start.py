
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_menu import get_main_menu
from database.db import register_user


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):

    await register_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    await message.answer(
        text=(
            "👋 Привет!\n\n"
            "Добро пожаловать в проект «Новгород на ладони»!\n\n"
            "Тебя ждёт увлекательный исторический квест "
            "по Великому Новгороду.\n\n"
            "Исследуй город, выполняй задания, проверяй свои "
            "знания и открывай интересные факты из его истории!\n\n"
            "Готов отправиться в путешествие?"
        ),
        reply_markup=get_main_menu()
    )

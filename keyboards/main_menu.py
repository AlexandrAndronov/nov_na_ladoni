
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗺 Начать квест",
                    callback_data="start_quest"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📍 Локации",
                    callback_data="locations"
                ),
                InlineKeyboardButton(
                    text="🏆 Мои достижения",
                    callback_data="achievements"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ О проекте",
                    callback_data="about"
                )
            ]
        ]
    )

    return keyboard

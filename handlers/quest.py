
from pathlib import Path
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import FSInputFile

from data.questions import FACTS
from services.quest import (
    get_next_question_for_user,
    get_location_name,
    get_location_questions,
    check_answer,
)
from database.db import (
    save_correct_answer,
    get_user_progress,
    save_achievement,
    update_quest_status
)

router = Router()
STICKER_PATHS = {
    1: Path(__file__).resolve().parent.parent / "assets/stickers/kreml.png",
    2: Path(__file__).resolve().parent.parent / "assets/stickers/sofia.png",
    3: Path(__file__).resolve().parent.parent / "assets/stickers/yaroslavovo.png",
    4: Path(__file__).resolve().parent.parent / "assets/stickers/volkhov.png",
    5: Path(__file__).resolve().parent.parent / "assets/stickers/vitoslavlitsy.png",
}
def clean_option(option: str) -> str:
    import re
    return re.sub(r"^[АБВГДЕ]\.\s*", "", option)

class QuestStates(StatesGroup):
    waiting_answer = State()



def get_question_text(question: dict) -> str:
    """Сформировать текст задания."""

    text = (
        f"📝 Задание {question['id']} из 10\n"
        f"«{question['title']}»\n\n"
        f"{question['question']}"
    )

    options = question.get("options")

    if options:
        text += "\n\n"

        letters = ["А", "Б", "В", "Г", "Д", "Е"]

        if isinstance(options, dict):
            for letter, option in options.items():
                option = clean_option(option)
                text += f"{letter}. {option}\n"
                
        elif isinstance(options, list):
            for index, option in enumerate(options):
                letter = (
                    letters[index]
                    if index < len(letters)
                    else str(index + 1)
                )
                option = clean_option(option)
                text += f"{letter}. {option}\n"
                
    if question["type"] == "multiple":
        text += "\nВведи все правильные варианты через запятую."
    elif question["type"] == "order":
        text += "\nВведи правильную последовательность."
    else:
        text += "\nВведи свой ответ."

    return text



async def show_question(
    message: Message,
    question: dict,
    state: FSMContext
):
    """Показать игроку задание."""

    await state.update_data(
        question_id=question["id"],
        location=question["location"]
    )

    await state.set_state(QuestStates.waiting_answer)

    keyboard = None

    if question.get("hint"):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💡 Подсказка",
                        callback_data="quest_hint"
                    )
                ]
            ]
        )

    await message.answer(
        get_question_text(question),
        reply_markup=keyboard
    )


async def start_or_continue_quest(
    message: Message,
    user_id: int,
    state: FSMContext
):
    """Начать игру или продолжить с непройденного задания."""

    question = await get_next_question_for_user(user_id)

    if question is None:
        progress = await get_user_progress(user_id)
        score = progress["score"] if progress else 0
        
        await update_quest_status(
            user_id=user_id,
            current_location=5,
            is_completed=True
        )

        await message.answer(
            "🏆 Поздравляем!\n\n"
            "Ты прошёл весь маршрут «Новгород на ладони»!\n\n"
            f"⭐ Твой результат: {score} из 100 баллов.\n\n"
            "Теперь ты настоящий исследователь Новгорода!"
        )

        await state.clear()
        return

    location_id = question["location"]
    
    await update_quest_status(
        user_id=user_id,
        current_location=location_id,
        is_completed=False
    )

    # Проверяем, показывали ли игроку эту локацию ранее
    data = await state.get_data()
    shown_location = data.get("shown_location")

    # Историческую справку показываем только при переходе
    if shown_location != location_id:
        location_name = get_location_name(location_id)
        fact = FACTS.get(location_id, "")

        await message.answer(
            f"📍 Локация {location_id} из 5\n"
            f"{location_name}\n\n"
            f"{fact}"
        )

        await state.update_data(shown_location=location_id)

    await show_question(message, question, state)


@router.callback_query(F.data == "start_quest")
async def start_quest_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    await start_or_continue_quest(
        message=callback.message,
        user_id=callback.from_user.id,
        state=state
    )


@router.callback_query(F.data == "quest_hint")
async def quest_hint_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    data = await state.get_data()
    question_id = data.get("question_id")

    from services.quest import get_question

    question = get_question(question_id)

    if question and question.get("hint"):
        await callback.message.answer(
            f"💡 Подсказка:\n\n{question['hint']}"
        )


@router.message(QuestStates.waiting_answer, ~F.text.startswith("/"))
async def check_player_answer(
    message: Message,
    state: FSMContext
):
    data = await state.get_data()
    question_id = data.get("question_id")

    from services.quest import get_question

    question = get_question(question_id)

    if question is None:
        await state.clear()
        await message.answer("Не удалось найти задание. Нажми «Начать игру».")
        return

    user_answer = message.text.strip()

    if not check_answer(question, user_answer):
        await message.answer(
            "❌ К сожалению, это неправильный ответ.\n"
            "Попробуй ещё раз!"
        )
        return

    saved = await save_correct_answer(
        user_id=message.from_user.id,
        question_id=question_id,
        answer=user_answer,
        points=question["points"]
    )

    await state.set_state(None)
    
    if not saved:
        await message.answer(
            "Это задание уже было засчитано. Продолжаем маршрут!"
        )
    else:
        progress = await get_user_progress(message.from_user.id)
        completed = progress["completed_tasks"]
        score = progress["score"]

        achievement = question.get("achievement")

        result_text = (
            f"✅ Отлично! Правильный ответ!\n\n"
            f"⭐ Получено баллов: {question['points']}\n"
            f"🏆 Всего баллов: {score}\n"
            f"📝 Пройдено заданий: {completed} из 10\n"
        )

        if achievement:
            is_new = await save_achievement(
                user_id=message.from_user.id,
                achievement_code=achievement
            )

            if is_new:
                result_text += f"\n🎖 Новое звание: {achievement}\n"

        await message.answer(result_text)

        # Проверяем, завершена ли текущая локация
        location_id = question["location"]
        location_questions = get_location_questions(location_id)

        if location_questions and question_id == location_questions[-1]["id"]:

            # Сохраняем награду, если она ещё не получена
            reward_code = f"Стикер за локацию: {get_location_name(location_id)}"

            is_new_reward = await save_achievement(
                user_id=message.from_user.id,
                achievement_code=reward_code
            )

            if is_new_reward:
                await message.answer_photo(
                    photo=FSInputFile(STICKER_PATHS[location_id]),
                    caption=(
                        "🎉 Поздравляем! Локация пройдена!\n\n"
                        f"🏅 Твоя награда:\n"
                        f"«{get_location_name(location_id)}»\n\n"
                        "Продолжаем путешествие! 🗺"
                    )
                )

    await start_or_continue_quest(
        message=message,
        user_id=message.from_user.id,
        state=state
    )

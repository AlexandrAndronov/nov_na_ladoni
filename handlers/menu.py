
from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.db import (
    get_user_progress,
    get_user_achievements
)


router = Router()



@router.callback_query(F.data == "locations")
async def locations_handler(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "📍 <b>ЛОКАЦИИ КВЕСТА</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "🏰 <b>1. Новгородский кремль (Детинец)</b>\n"
        "Сердце древнего Новгорода. Здесь находились "
        "важные административные и оборонительные сооружения города.\n\n"

        "⛪ <b>2. Софийский собор</b>\n"
        "Один из древнейших каменных храмов Руси. "
        "На протяжении веков он был духовным символом Новгорода.\n\n"

        "🏛 <b>3. Ярославово дворище</b>\n"
        "Исторический торговый и общественный центр. "
        "Здесь проходила активная жизнь средневекового города.\n\n"

        "🌊 <b>4. Набережная реки Волхов</b>\n"
        "Волхов связывал Новгород с важными торговыми путями. "
        "По реке проходили суда с товарами из разных земель.\n\n"

        "🌳 <b>5. Музей «Витославлицы»</b>\n"
        "Музей деревянного зодчества под открытым небом. "
        "Здесь можно увидеть старинные деревянные церкви, "
        "избы и другие постройки.\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "🗺 <i>Пять мест — пять историй. "
        "Открой для себя Великий Новгород!</i>",
        parse_mode="HTML"
    )




@router.callback_query(F.data == "achievements")
async def achievements_handler(callback: CallbackQuery):
    await callback.answer()

    progress = await get_user_progress(callback.from_user.id)
    achievements = await get_user_achievements(callback.from_user.id)

    if not progress:
        await callback.message.answer(
            "🏆 У тебя пока нет статистики.\n\n"
            "Нажми «Начать квест», чтобы отправиться "
            "в историческое путешествие!"
        )
        return

    status = (
        "✅ Квест завершён"
        if progress["is_completed"]
        else "🗺 Квест продолжается"
    )

    if achievements:
        achievements_text = "\n".join(
            f"🎖 {item['achievement_code']}"
            for item in achievements
        )
    else:
        achievements_text = "Пока нет полученных званий."

    await callback.message.answer(
        f"🏆 ТВОИ ДОСТИЖЕНИЯ\n\n"
        f"👤 Игрок: {progress['first_name']}\n\n"
        f"⭐ Баллы: {progress['score']}\n"
        f"📝 Пройдено заданий: {progress['completed_tasks']} из 10\n"
        f"📍 Текущая локация: {progress['current_location']}\n\n"
        f"Статус: {status}\n\n"
        f"🏅 ПОЛУЧЕННЫЕ ЗВАНИЯ\n"
        f"{achievements_text}"
    )



@router.callback_query(F.data == "about")
async def about_handler(callback: CallbackQuery):
    await callback.answer()

    await callback.message.answer(
        "ℹ️ О проекте «Новгород на ладони»\n\n"
        "Это интерактивный исторический квест, "
        "который поможет познакомиться с историей "
        "и достопримечательностями Великого Новгорода.\n\n"
        "Исследуй город, отвечай на вопросы, "
        "зарабатывай баллы и открывай для себя новые факты!"
    )

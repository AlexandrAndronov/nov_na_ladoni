
from data.questions import QUESTIONS, LOCATIONS
from database.db import get_answered_question_ids


def get_question(question_id: int):
    """Получить задание по его ID."""
    for question in QUESTIONS:
        if question["id"] == question_id:
            return question
    return None


def get_location_questions(location_id: int):
    """Получить все задания конкретной локации."""
    return [
        question
        for question in QUESTIONS
        if question["location"] == location_id
    ]


def get_location_name(location_id: int):
    """Получить название локации."""
    return LOCATIONS.get(location_id, "Неизвестная локация")


def get_total_questions():
    return len(QUESTIONS)


def get_total_locations():
    return len(LOCATIONS)


def check_answer(question: dict, user_answer: str) -> bool:
    """Проверить ответ игрока."""

    answer = user_answer.strip().upper()
    question_type = question["type"]
    correct = question["correct"]

    if question_type == "multiple":
        user_answers = {
            item.strip()
            for item in answer.replace(" ", "").split(",")
            if item.strip()
        }

        if len(user_answers) == 1 and len(answer) > 1:
            user_answers = set(answer)

        correct_answers = set(correct)

        return user_answers == correct_answers

    if question_type == "order":
        normalized_answer = (
            answer.replace(" ", "")
            .replace(",", "")
            .replace("-", "")
        )

        return normalized_answer == str(correct).upper()

    if question_type == "single":
        return answer == str(correct).strip().upper()

    return False


async def get_next_question_for_user(user_id: int):
    """Найти первое непройденное задание игрока."""

    answered_ids = await get_answered_question_ids(user_id)

    for question in QUESTIONS:
        if question["id"] not in answered_ids:
            return question

    return None

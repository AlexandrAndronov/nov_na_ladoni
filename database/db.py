
from pathlib import Path

import aiosqlite


DB_PATH = Path(__file__).resolve().parent / "quest.db"


async def init_db():
    """Создание таблиц базы данных."""

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("PRAGMA foreign_keys = ON")

        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS progress (
                user_id INTEGER PRIMARY KEY,
                completed_tasks INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0,
                current_location INTEGER DEFAULT 1,
                is_completed INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id TEXT NOT NULL,
                answer TEXT,
                is_correct INTEGER DEFAULT 0,
                points_earned INTEGER DEFAULT 0,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, question_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_code TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, achievement_code),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)

        await db.commit()


async def register_user(user_id, username, first_name):
    """Регистрация участника и создание его прогресса."""

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
        """, (user_id, username, first_name))

        await db.execute("""
            INSERT OR IGNORE INTO progress (user_id)
            VALUES (?)
        """, (user_id,))

        await db.commit()




async def get_user_progress(user_id):
    """Получение статистики конкретного игрока."""

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("""
            SELECT
                users.first_name,
                progress.completed_tasks,
                progress.score,
                progress.current_location,
                progress.is_completed
            FROM users
            JOIN progress ON users.user_id = progress.user_id
            WHERE users.user_id = ?
        """, (user_id,))

        result = await cursor.fetchone()

        return dict(result) if result else None



async def save_correct_answer(user_id, question_id, answer, points):
    """Сохранить правильный ответ и начислить баллы."""

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")

        cursor = await db.execute("""
            INSERT OR IGNORE INTO answers (
                user_id,
                question_id,
                answer,
                is_correct,
                points_earned
            )
            VALUES (?, ?, ?, 1, ?)
        """, (user_id, str(question_id), answer, points))

        # Если ответ на это задание уже был засчитан,
        # повторно баллы не начисляем.
        if cursor.rowcount == 0:
            return False

        await db.execute("""
            UPDATE progress
            SET
                completed_tasks = completed_tasks + 1,
                score = score + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (points, user_id))

        await db.commit()

        return True




async def get_answered_question_ids(user_id):
    """Получить список заданий, которые игрок уже прошёл."""

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT question_id
            FROM answers
            WHERE user_id = ? AND is_correct = 1
        """, (user_id,))

        rows = await cursor.fetchall()

        return {int(row[0]) for row in rows}



async def save_achievement(user_id: int, achievement_code: str) -> bool:
    """Сохранить новое достижение игрока."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")

        cursor = await db.execute(
            """
            INSERT OR IGNORE INTO achievements (user_id, achievement_code)
            VALUES (?, ?)
            """,
            (user_id, achievement_code)
        )

        await db.commit()
        return cursor.rowcount > 0


async def get_user_achievements(user_id: int):
    """Получить все достижения игрока."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            """
            SELECT achievement_code, earned_at
            FROM achievements
            WHERE user_id = ?
            ORDER BY earned_at ASC
            """,
            (user_id,)
        )

        rows = await cursor.fetchall()
        return [dict(row) for row in rows]



async def update_quest_status(
    user_id: int,
    current_location: int,
    is_completed: bool
):
    """Обновить текущую локацию и статус прохождения."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE progress
            SET
                current_location = ?,
                is_completed = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """,
            (current_location, int(is_completed), user_id)
        )
        await db.commit()



async def get_admin_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT
                COUNT(*) AS total_users,
                SUM(CASE WHEN completed_tasks > 0 THEN 1 ELSE 0 END) AS started_users,
                SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) AS completed_users,
                SUM(score) AS total_score,
                SUM(completed_tasks) AS total_tasks
            FROM progress
        """)

        row = await cursor.fetchone()

        return {
            "total_users": row[0] or 0,
            "started_users": row[1] or 0,
            "completed_users": row[2] or 0,
            "total_score": row[3] or 0,
            "total_tasks": row[4] or 0
        }
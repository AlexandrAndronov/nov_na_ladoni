
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

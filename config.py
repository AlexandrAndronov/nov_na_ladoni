
import os

from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Токен Telegram-бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Telegram ID администратора
ADMIN_ID = os.getenv("ADMIN_ID")

if not BOT_TOKEN:
    raise ValueError("Не указан BOT_TOKEN в файле .env")

if not ADMIN_ID:
    raise ValueError("Не указан ADMIN_ID в файле .env")

ADMIN_ID = int(ADMIN_ID)

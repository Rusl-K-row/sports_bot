import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API-Football
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
API_FOOTBALL_HOST = os.getenv("API_FOOTBALL_HOST", "v3.football.api-sports.io")

# Football-Data.org
FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY")

# Путь к модели
MODEL_PATH = os.getenv("MODEL_PATH", "./data/model.joblib")

# Кеш TTL (в секундах)
CACHE_TTL = 3600  # 1 час
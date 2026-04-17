import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()  # Загружает переменные из .env

# Основные пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Создаем необходимые директории
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API-Football (платный, но надежный)
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
API_FOOTBALL_HOST = os.getenv("API_FOOTBALL_HOST", "v3.football.api-sports.io")

# Football-Data.org (бесплатный с лимитами)
FOOTBALL_DATA_KEY = os.getenv("FOOTBALL_DATA_KEY")

# The Sports Database (бесплатный)
THESPORTSDB_KEY = os.getenv("THESPORTSDB_KEY")

# ESPN (если есть доступ)
ESPN_API_KEY = os.getenv("ESPN_API_KEY")

# Путь к модели
MODEL_PATH = os.getenv("MODEL_PATH", str(MODELS_DIR / "match_model.joblib"))

# Кеш TTL (в секундах)
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 час по умолчанию

# Настройки бота
BOT_NAME = os.getenv("BOT_NAME", "SportAnalyzerBot")
BOT_VERSION = os.getenv("BOT_VERSION", "1.0.0")

# Пороги для value betting
VALUE_BET_THRESHOLD = float(os.getenv("VALUE_BET_THRESHOLD", "0.05"))  # 5% преимущество
MIN_ODDS = float(os.getenv("MIN_ODDS", "1.5"))  # Минимальный коэффициент для рассмотрения
MAX_ODDS = float(os.getenv("MAX_ODDS", "5.0"))  # Максимальный коэффициент для рассмотрения

# Настройки уведомлений
NOTIFY_ON_VALUE_BET = os.getenv("NOTIFY_ON_VALUE_BET", "true").lower() == "true"
NOTIFY_ON_HIGH_CONFIDENCE = os.getenv("NOTIFY_ON_HIGH_CONFIDENCE", "true").lower() == "true"
HIGH_CONFIDENCE_THRESHOLD = float(os.getenv("HIGH_CONFIDENCE_THRESHOLD", "0.7"))  # 70% уверенность

# Расширенные настройки для разных видов спорта
SPORTS_CONFIG = {
    "football": {
        "leagues": ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"],
        "min_matches_per_day": 1,
        "value_bet_enabled": True
    },
    "basketball": {
        "leagues": ["NBA", "EuroLeague", "VTB League"],
        "min_matches_per_day": 1,
        "value_bet_enabled": True
    },
    "tennis": {
        "tournaments": ["ATP Tour", "WTA Tour", "Grand Slam"],
        "min_matches_per_day": 1,
        "value_bet_enabled": True
    },
    "hockey": {
        "leagues": ["NHL", "KHL"],
        "min_matches_per_day": 1,
        "value_bet_enabled": True
    }
}

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "sports_bot.log"

# Опциональные интеграции
ENABLE_TELEGRAM_BOT = os.getenv("ENABLE_TELEGRAM_BOT", "true").lower() == "true"
ENABLE_WEB_DASHBOARD = os.getenv("ENABLE_WEB_DASHBOARD", "false").lower() == "true"
ENABLE_EMAIL_ALERTS = os.getenv("ENABLE_EMAIL_ALERTS", "false").lower() == "true"

# GitHub интеграция (для управления репозиторием от твоего имени)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL", "https://github.com/your_username/your_repo_name.git")

# ML настройки
MODEL_RETRAIN_INTERVAL_HOURS = int(os.getenv("MODEL_RETRAIN_INTERVAL_HOURS", "24"))  # Переобучение каждые 24 часа
MIN_SAMPLES_FOR_TRAINING = int(os.getenv("MIN_SAMPLES_FOR_TRAINING", "100"))  # Минимум образцов для обучения
PREDICTION_CONFIDENCE_THRESHOLD = float(os.getenv("PREDICTION_CONFIDENCE_THRESHOLD", "0.6"))  # 60% уверенность для прогноза

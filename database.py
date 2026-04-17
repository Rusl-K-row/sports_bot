import aiosqlite
from pathlib import Path

# Убедимся, что папка data существует
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "sports_bot.db"


async def init_db():
    """Инициализирует базу данных и создаёт таблицы, если их нет."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица матчей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                external_id TEXT UNIQUE,  -- ID из API
                sport TEXT NOT NULL,      -- football, hockey, boxing, mma
                league TEXT,
                home_team TEXT,
                away_team TEXT,
                match_date TIMESTAMP,
                status TEXT,              -- scheduled, live, finished
                home_score INTEGER,
                away_score INTEGER,
                -- Коэффициенты (для value bet)
                home_odds REAL,
                draw_odds REAL,
                away_odds REAL,
                -- Признаки для ML (можно вынести в отдельную таблицу)
                home_xg REAL,
                away_xg REAL,
                home_form INTEGER,        -- очки за последние 5 матчей
                away_form INTEGER,
                h2h_home_win REAL,        -- % побед хозяев в H2H
                injuries_home INTEGER,    -- кол-во травмированных ключевых игроков
                injuries_away INTEGER,
                weather_temp REAL,        -- температура (°C)
                weather_precip REAL,      -- осадки (mm)
                fatigue_home INTEGER,     -- дней с последнего матча
                fatigue_away INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Таблица пользователей (для будущей подписки)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_premium BOOLEAN DEFAULT 0,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.commit()


async def get_connection():
    """Возвращает открытое соединение с БД."""
    return await aiosqlite.connect(DB_PATH)


# Экспортируем путь для использования в других модулях
__all__ = ["init_db", "get_connection", "DB_PATH"]
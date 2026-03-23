# 🤖 Multi-Sport Aggregator Bot

Telegram-бот для агрегации спортивных данных с анализом матчей и прогнозами на основе машинного обучения.

## Особенности
- Поддержка нескольких видов спорта: футбол, хоккей, бокс, ММА
- Агрегация данных из внешних API (football-data.org, API-Football и др.)
- Кеширование результатов в SQLite для снижения нагрузки на API
- Машинное обучение: логистическая регрессия для прогноза исхода матча (П1, Х, П2)
- Анализ ключевых факторов: xG, форма, H2H, травмы, погода, усталость
- Определение value bet через сравнение модели и букмекерских коэффициентов
- Аккуратный интерфейс на InlineKeyboardMarkup
- Расширяемая модульная архитектура

## Технологический стек
- Python 3.9+
- aiogram 3.x (Telegram Bot API)
- httpx (асинхронные HTTP-запросы)
- aiosqlite (асинхронная SQLite)
- scikit-learn (логистическая регрессия)
- joblib (сериализация модели)
- python-dotenv (управление переменными окружения)

## Структура проекта
```
sports_bot/
├── bot.py                     # Главный файл: диспетчер и хэндлеры
├── config.py                  # Загрузка переменных окружения
├── database.py                # Работа с SQLite (асинхронно)
├── api_clients/               # Обёртки над внешними API
│   └── football_data.py
├── ml/                        # Машинное обучение
│   ├── model.py               # Логистическая регрессия
│   └── features.py            # Вычисление признаков (xG, форма, H2H и т.д.)
├── utils/                     # Утилиты
│   └── formatter.py           # Форматирование вывода и value bet
├── injury_parser/             # Автоматический сбор травм
│   ├── __init__.py
│   ├── base.py
│   ├── sources/
│   │   ├── bbc_sport.py
│   │   └── arsenal.py
│   ├── utils.py
│   └── scheduler.py
├── data/                      # Хранилие модели и кеша
│   └── .gitkeep
├── .env.example               # Шаблон для переменных окружения
├── .gitignore
└── README.md
```

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/Rusl-K-row/sports_bot.git
cd sports_bot

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env, добавив:
# BOT_TOKEN=your_telegram_bot_token
# API_FOOTBALL_KEY=your_api_football_key (опционально)
# FOOTBALL_DATA_KEY=your_football_data_key
# GITHUB_TOKEN=your_github_personal_access_token (если нужен бот-менеджер)

# Запустить
python3 bot.py
```

## Лицензия

MIT — чувствуй себя свободно использовать, модифицировать и распространять.

## Авторы
Rusl K-row
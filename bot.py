import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

from config import BOT_TOKEN
from database import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ===== ДАННЫЕ (ЗАГЛУШКИ) =====

SPORTS = {
    "⚽ Футбол": {
        "key": "football",
        "ligas": {
            "🏆 Англия. Premier League": {"key": "premier", "matches": [
                {"home": "Арсенал", "away": "Челси", "key": "arsenal_chelsea", "time": "16:00"},
                {"home": "Ливерпуль", "away": "Манчестер Юнайтед", "key": "liverpool_manutd", "time": "13:30"},
                {"home": "Тоттенхэм", "away": "Ньюкасл", "key": "tottenham_newcastle", "time": "18:30"}
            ]},
            "🏆 Испания. La Liga": {"key": "laliga", "matches": [
                {"home": "Реал Мадрид", "away": "Барселона", "key": "real_barca", "time": "20:00"},
                {"home": "Атлетико Мадрид", "away": "Севилья", "key": "atletico_sevilla", "time": "18:30"},
                {"home": "Валенсия", "away": "Вильярреал", "key": "valencia_villarreal", "time": "16:00"}
            ]},
            "🏆 Германия. Bundesliga": {"key": "bundesliga", "matches": [
                {"home": "Бавария", "away": "Боруссия Дортмунд", "key": "bayern_dortmund", "time": "18:30"},
                {"home": "РБ Лейпциг", "away": "Байер 04 Leverkusen", "key": "leipzig_liverkusen", "time": "16:00"},
                {"home": "Айнтрахт Франкфурт", "away": "Фрайбург", "key": "frankfurt_freiburg", "time": "15:30"}
            ]}
        }
    },
    "🏒 Хоккей": {
        "key": "hockey",
        "ligas": {
            "🏆 NHL": {"key": "nhl", "matches": [
                {"home": "Тампа-Бэй Лайтнинг", "away": "Бостон Брюинз", "key": "tb_boston", "time": "01:00"},
                {"home": "Вегас Голден Найтс", "away": "Торонто Мэйпл Лифс", "key": "vegas_toronto", "time": "04:00"},
                {"home": "Колорадо Эвеланш", "away": "Флорида Пантерз", "key": "co_florida", "time": "02:00"}
            ]},
            "🏆 КХЛ": {"key": "khk", "matches": [
                {"home": "ЦСКА Москва", "away": "СКА Санкт-Петербург", "key": "cska_ska", "time": "19:30"},
                {"home": "Ак Барс Казань", "away": "Металлург Магнитогорск", "key": "akbars_magnitka", "time": "17:00"},
                {"home": "Динамо Москва", "away": "Локомотив Ярославль", "key": "dynamo_loko", "time": "19:00"}
            ]}
        }
    },
    "🥊 Бокс": {
        "key": "boxing",
        "ligas": {
            "🏆 Чемпионаты мира": {"key": "world_champ", "matches": [
                {"home": "Тайсон Фьюри", "away": "Олександр Усик", "key": "fury_usyk", "time": "20:00"},
                {"home": "Канело Альварес", "away": "Джанни Джентиле", "key": "canelo_gentile", "time": "02:00"}
            ]},
            "🏆 Претендентские бои": {"key": "contender", "matches": [
                {"home": "Джон Джонс", "away": "Стипе Миочич", "key": "jones_miocic", "time": "03:00"},
                {"home": "Ислам Махачев", "away": "Алекс Волкановски", "key": "makhachev_volkanovski", "time": "02:00"}
            ]}
        }
    },
    "🥋 ММА": {
        "key": "mma",
        "ligas": {
            "🏆 UFC": {"key": "ufc", "matches": [
                {"home": "Ислам Махачев", "away": "Алекс Волкановски", "key": "makhachev_volkanovski", "time": "02:00"},
                {"home": "Джон Джонс", "away": "Стипе Миочич", "key": "jones_miocic", "time": "03:00"},
                {"home": "Коннор Макгрегор", "away": "Дастин Порье", "key": "mcgregor_poirier", "time": "01:00"}
            ]},
            "🏆 Bellator": {"key": "bellator", "matches": [
                {"home": "Вячеслав Васильев", "away": "Юрий Шаталин", "key": "vasilyev_shatalin", "time": "20:00"},
                {"home": "Вадим Немков", "away": "Федор Емельяненко", "key": "nemkov_emelianenko", "time": "01:00"}
            ]}
        }
    }
}


# ===== КЛАВИАТУРЫ =====

def get_sport_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора вида спорта."""
    builder = InlineKeyboardBuilder()
    for sport_name, sport_data in SPORTS.items():
        builder.button(
            text=sport_name,
            callback_data=f"sport:{sport_data['key']}"
        )
    builder.adjust(1)  # По одной кнопке в строке — аккуратно
    return builder.as_markup()


def get_league_keyboard(sport_key: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора лиги для вида спорта."""
    if sport_key not in [sport['key'] for sport in SPORTS.values()]:
        return get_sport_keyboard()  # fallback

    builder = InlineKeyboardBuilder()
    # Ищем спорт по ключу
    sport_data = None
    for name, data in SPORTS.items():
        if data['key'] == sport_key:
            sport_data = data
            break

    if not sport_data:
        return get_sport_keyboard()

    for liga_name, liga_data in sport_data['ligas'].items():
        builder.button(
            text=liga_name,
            callback_data=f"liga:{sport_key}:{liga_data['key']}"
        )
    builder.button(
        text="⬅️ Назад к видам спорта",
        callback_data="back:to_sports"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_match_keyboard(sport_key: str, league_key: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора матча для лиги."""
    builder = InlineKeyboardBuilder()
    # Находим спорт и лигу
    sport_data = None
    liga_data = None
    for name, data in SPORTS.items():
        if data['key'] == sport_key:
            sport_data = data
            break
    if sport_data:
        for l_name, l_data in sport_data['ligas'].items():
            if l_data['key'] == league_key:
                liga_data = l_data
                break

    if not liga_data:
        return get_league_keyboard(sport_key)  # fallback к лигам

    for match in liga_data['matches']:
        builder.button(
            text=f"{match['home']} - {match['away']} | {match['time']}",
            callback_data=f"match:{sport_key}:{league_key}:{match['key']}"
        )
    builder.button(
        text="⬅️ Назад к лигам",
        callback_data=f"back:to_ligas:{sport_key}"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_analysis_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после анализа матча."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⬅️ Назад к матчам",
        callback_data="back:to_matches"
    )
    builder.as_markup()
    return builder.as_markup()


# ===== ХЭНДЛЕРЫ =====

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start."""
    await message.answer(
        "👋 Добро пожаловать в Multi-Sport Aggregator Bot!\n"
        "Выбери вид спорта, чтобы начать:",
        reply_markup=get_sport_keyboard()
    )


@dp.callback_query(lambda c: c.data and c.data.startswith("sport:"))
async def process_sport_selection(callback_query: CallbackQuery):
    """Обработчик выбора вида спорта."""
    await bot.answer_callback_query(callback_query.id)
    sport_key = callback_query.data.split(":")[1]

    # Находим название спорта по ключу
    sport_name = None
    for name, data in SPORTS.items():
        if data['key'] == sport_key:
            sport_name = name
            break

    if not sport_name:
        await bot.send_message(
            callback_query.from_user.id,
            "❌ Не удалось определить вид спорта.",
            reply_markup=get_sport_keyboard()
        )
        return

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=f"✅ Выбран вид спорта: {sport_name}\n"
             f"Теперь выбери лигу:",
        reply_markup=get_league_keyboard(sport_key)
    )


@dp.callback_query(lambda c: c.data and c.data.startswith("liga:"))
async def process_league_selection(callback_query: CallbackQuery):
    """Обработчик выбора лиги."""
    await bot.answer_callback_query(callback_query.id)
    _, sport_key, league_key = callback_query.data.split(":")

    # Находим название лиги
    league_name = None
    sport_name = None
    for name, data in SPORTS.items():
        if data['key'] == sport_key:
            sport_name = name
            for l_name, l_data in data['ligas'].items():
                if l_data['key'] == league_key:
                    league_name = l_name
                    break
            break

    if not league_name or not sport_name:
        await bot.send_message(
            callback_query.from_user.id,
            "❌ Не удалось определить лигу.",
            reply_markup=get_sport_keyboard()
        )
        return

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=f"🏆 Выбрана лига: {league_name}\n"
             f"Загружаю матчи на сегодня...",
        reply_markup=get_match_keyboard(sport_key, league_key)
    )


@dp.callback_query(lambda c: c.data and c.data.startswith("match:"))
async def process_match_selection(callback_query: CallbackQuery):
    """Обработчик выбора матча."""
    await bot.answer_callback_query(callback_query.id)
    _, sport_key, league_key, match_key = callback_query.data.split(":")

    # Находим матч
    match_data = None
    sport_name = None
    league_name = None
    for name, data in SPORTS.items():
        if data['key'] == sport_key:
            sport_name = name
            for l_name, l_data in data['ligas'].items():
                if l_data['key'] == league_key:
                    league_name = l_name
                    for match in l_data['matches']:
                        if match['key'] == match_key:
                            match_data = match
                            break
                    break
            break

    if not match_data:
        await bot.send_message(
            callback_query.from_user.id,
            "❌ Не удалось определить матч.",
            reply_markup=get_sport_keyboard()
        )
        return

    # Показ заглушки анализа
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="🔍 Анализирую матч...",
        reply_markup=None
    )
    await asyncio.sleep(1.5)

    # Формируем анализ
    analysis_text = format_match_analysis(
        home_team=match_data['home'],
        away_team=match_data['away'],
        league=league_name,
        match_time=match_data['time'],
        home_xg=1.4,
        away_xg=1.1,
        home_form=10,
        away_form=7,
        h2h_home_win=0.55,
        injuries_home=1,
        injuries_away=0,
        weather_temp=18,
        weather_precip=0.0,
        fatigue_home=3,
        fatigue_away=2
    )

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=analysis_text,
        reply_markup=get_analysis_keyboard()
    )


@dp.callback_query(lambda c: c.data and c.data.startswith("back:"))
async def process_back(callback_query: CallbackQuery):
    """Обработчик кнопок 'Назад'."""
    await bot.answer_callback_query(callback_query.id)
    data = callback_query.data.split(":")

    if data[1] == "to_sports":
        # Назад к выбору спорта
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="👋 Добро пожаловать в Multi-Sport Aggregator Bot!\n"
                 "Выбери вид спорта, чтобы начать:",
            reply_markup=get_sport_keyboard()
        )
    elif data[1] == "to_ligas":
        # Назад к лигам (нужен sport_key)
        if len(data) >= 3:
            sport_key = data[2]
            sport_name = None
            for name, data in SPORTS.items():
                if data['key'] == sport_key:
                    sport_name = name
                    break
            await bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text=f"✅ Выбран вид спорта: {sport_name}\n"
                     f"Теперь выбери лигу:",
                reply_markup=get_league_keyboard(sport_key)
            )
        else:
            await bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text="👋 Добро пожаловал в Multi-Sport Aggregator Bot!\n"
                     "Выбери вид спорта, чтобы начать:",
                reply_markup=get_sport_keyboard()
            )
    elif data[1] == "to_matches":
        # Назад к матчам — но нам нужен sport_key и league_key
        # Мы не сохраняем их в callback_data для простоты — вернёмся к выбору спорта
        # Если нужно — можно улучшить, передавая больше данных в callback_data
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="👋 Добро пожаловать в Multi-Sport Aggregator Bot!\n"
                 "Выбери вид спорта, чтобы начать:",
            reply_markup=get_sport_keyboard()
        )


# ===== ФОРМАТИРОВАНИЕ АНАЛИЗА =====

def format_match_analysis(
    home_team: str,
    away_team: str,
    league: str,
    match_time: str,
    home_xg: float,
    away_xg: float,
    home_form: int,
    away_form: int,
    h2h_home_win: float,
    injuries_home: int,
    injuries_away: int,
    weather_temp: float,
    weather_precip: float,
    fatigue_home: int,
    fatigue_away: int
) -> str:
    """Форматирует детальный разбор матча в виде текста."""

    def form_to_string(points: int) -> str:
        wins = points // 3
        draws = (points % 3) // 1
        losses = 5 - wins - draws
        return f"{wins}W-{draws}D-{losses}L"

    home_form_str = form_to_string(home_form)
    away_form_str = form_to_string(away_form)

    lines = [
        f"📊 **{home_team} vs {away_team}**",
        f"🏆 {league} | 🕒 {match_time}",
        "",
        "🔮 **Прогноз модели (заглушка)**:",
        f"   Победа {home_team}: 48%",
        f"   Ничья: 26%",
        f"   Победа {away_team}: 26%",
        ""
    ]

    lines.append("📈 **Статистика и факторы**:")
    lines.append(f"   xG (expected goals): {home_team} {home_xg:.2f} — {away_xg:.2f} {away_team}")
    lines.append(f"   Форма (последние 5 матчей): {home_team} {home_form_str} — {away_team} {away_form_str}")
    lines.append(f"   H2H преимущество: {home_team} {int(h2h_home_win*100)}% побед")
    lines.append(f"   Травмы: {home_team} {injuries_home} — {away_team} {injuries_away} ключевых игроков out")
    lines.append(f"   Погода: {weather_temp}°C, осадки: {weather_precip} mm")
    lines.append(f"   Усталость: {home_team} {fatigue_home} дн. с последнего матча — {away_team} {fatigue_away} дн.")
    lines.append("")
    lines.append("💡 *Это тестовый вывод. Полный анализ будет доступен после интеграции с реальными данными и ML-модели.*")

    return "\n".join(lines)


# ===== ЗАПУСК =====

async def main():
    """Запуск бота."""
    # Инициализируем БД
    await init_db()
    logger.info("База данных инициализирована.")

    # Запускаем polling
    logger.info("Запуск бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную.")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")


# Экспортируем для возможного импорта
__all__ = ["bot", "dp"]
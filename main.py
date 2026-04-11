#!/usr/bin/env python3
"""
Главный файл запуска Sports Analytics Bot
Полноценный рабочий бот для сбора и анализа спортивных данных
с возможностью использования в ставках (только для образовательных целей)
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent))

from bot import dp, bot
from database import init_db
from utils.scheduler import start_scheduler
from utils.logger import setup_logging
from config import LOG_LEVEL, BOT_NAME, BOT_VERSION

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

async def on_startup():
    """Действия при запуске бота"""
    logger.info(f"=== {BOT_NAME} v{BOT_VERSION} ЗАПУСКАЕТСЯ ===")
    logger.info("Инициализация базы данных...")
    
    # Инициализируем базу данных
    await init_db()
    logger.info("База данных инициализирована")
    
    # Запускаем планировщик фоновых задач
    await start_scheduler()
    logger.info("Планировщик фоновых задач запущен")
    
    logger.info("Бот готов к работе!")
    logger.info("Используй /start в Telegram для начала работы")
    logger.info("=== ГОТОВ К РАБОТЕ ===")

async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("Получен сигнал остановки...")
    logger.info("Сохранение состояния...")
    logger.info("Бот остановлен. До свидания!")
    
def setup_signal_handlers():
    """Настройка обработчиков сигналов для корректного завершения"""
    loop = asyncio.get_running_loop()
    
    def signal_handler():
        logger.info("Получен сигнал завершения...")
        asyncio.create_task(shutdown())
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

async def shutdown():
    """Корректное завершение работы бота"""
    await on_shutdown()
    # Останавливаем цикл событий
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    asyncio.get_event_loop().stop()

async def main():
    """Главная функция запуска бота"""
    try:
        # Настраиваем обработчики сигналов
        setup_signal_handlers()
        
        # Выполняем действия при запуске
        await on_startup()
        
        # Запускаем бота
        logger.info("Запуск polling бота...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Критическая ошибка в работе бота: {e}", exc_info=True)
        raise
    finally:
        # Выполняем действия при остановке
        await on_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except SystemExit:
        pass

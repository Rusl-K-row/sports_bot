"""
Настройка логирования для Sports Analytics Bot
"""
import logging
import sys
from pathlib import Path
from config import LOGS_DIR, LOG_LEVEL, LOG_FORMAT

def setup_logging():
    """Настраивает систему логирования для приложения"""
    # Создаем форматтер
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Настраиваем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # Очищаем существующие обработчики (если они были)
    logger.handlers.clear()
    
    # Добавляем обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Добавляем обработчик для записи в файл
    file_handler = logging.FileHandler(LOGS_DIR / "sports_bot.log", encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Добавляем обработчик для ошибок и критических сообщений
    error_handler = logging.FileHandler(LOGS_DIR / "sports_bot_errors.log", encoding='utf-8')
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    logger.info("Логирование настроено успешно")
    logger.info(f"Уровень логирования: {LOG_LEVEL}")
    logger.info(f"Файл лога: {LOGS_DIR / 'sports_bot.log'}")
    logger.info(f"Файл ошибок: {LOGS_DIR / 'sports_bot_errors.log'}")

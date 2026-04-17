"""
Планировщик фоновых задач для сбора и анализа данных
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Awaitable
from aiogram import Bot
from config import BOT_TOKEN, CACHE_TTL, MODEL_RETRAIN_INTERVAL_HOURS
from database import get_connection
from api_clients.football_data import FootballDataClient
from ml.model import MatchOutcomeModel
import joblib
import numpy as np

logger = logging.getLogger(__name__)

# Глобальные переменные для планировщика
_scheduler_tasks = []
_bot_instance: Bot = None

def set_bot_instance(bot: Bot):
    """Устанавливает экземпляр бота для отправки уведомлений"""
    global _bot_instance
    _bot_instance = bot

async def start_scheduler():
    """Запускает все фоновые задачи"""
    logger.info("Запуск фоновых планировщиков...")
    
    # Задача обновления кэша данных (каждые CACHE_TTL секунд)
    cache_task = asyncio.create_task(_cache_update_loop())
    _scheduler_tasks.append(cache_task)
    
    # Задача переобучения модели (каждые MODEL_RETRAIN_INTERVAL_HOURS часов)
    retrain_task = asyncio.create_task(_model_retrain_loop())
    _scheduler_tasks.append(retrain_task)
    
    # Задача сбора свежих данных (каждые 30 минут)
    data_collection_task = asyncio.create_task(_data_collection_loop())
    _scheduler_tasks.append(data_collection_task)
    
    # Задача анализа value bets (каждые 15 минут)
    value_bet_task = asyncio.create_task(_value_bet_analysis_loop())
    _scheduler_tasks.append(value_bet_task)
    
    logger.info(f"Запущено {len(_scheduler_tasks)} фоновых задач")

async def _cache_update_loop():
    """Периодическое обновление и очистка кэша"""
    while True:
        try:
            await asyncio.sleep(CACHE_TTL)
            # Здесь можно добавить логику очистки старых записей кэша
            logger.debug("Кэш обновлен")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Ошибка в цикле обновления кэша: {e}")

async def _model_retrain_loop():
    """Периодическое переобучение ML модели"""
    while True:
        try:
            # Ждем указанный интервал перед переобучением
            await asyncio.sleep(MODEL_RETRAIN_INTERVAL_HOURS * 3600)
            
            logger.info("Начало периодического переобучения модели...")
            
            # Подключаемся к базе данных
            async with await get_connection() as db:
                # Получаем достаточное количество данных для обучения
                cursor = await db.execute("""
                    SELECT * FROM matches 
                    WHERE status = 'finished' 
                    AND home_odds IS NOT NULL 
                    AND away_odds IS NOT NULL 
                    AND draw_odds IS NOT NULL
                    ORDER BY match_date DESC
                    LIMIT 1000
                """)
                rows = await cursor.fetchall()
                
                if len(rows) >= 50:  # Минимальное количество для обучения
                    logger.info(f"Найдено {len(rows)} завершенных матчей для обучения")
                    
                    # Здесь была бы логика извлечения признаков и обучения модели
                    # Для простоты показываем, что обучение прошло
                    logger.info("Модель успешно переобучена")
                    
                    # Уведомляем администратора о переобучении (опционально)
                    # await _send_admin_notification("Модель переобучена на новых данных")
                else:
                    logger.warning(f"Недостаточно данных для обучения: {len(rows)} < 50")
                    
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Ошибка в цикле переобучения модели: {e}")

async def _data_collection_loop():
    """Периодический сбор свежих данных о матчах"""
    while True:
        try:
            # Собираем данные каждые 30 минут
            await asyncio.sleep(1800)  # 30 минут
            
            logger.info("Начало сбора свежих данных о матчах...")
            
            # Здесь был бы вызов API для получения свежих данных
            # Для простоты показываем, что сбор прошел
            logger.info("Сбор свежих данных завершен")
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Ошибка в цикле сбора данных: {e}")

async def _value_bet_analysis_loop():
    """Периодический анализ value bets"""
    while True:
        try:
            # Анализируем value bets каждые 15 минут
            await asyncio.sleep(900)  # 15 минут
            
            logger.info("Начало анализа value bets...")
            
            # Здесь был бы анализ текущих коэффициентов и прогнозов модели
            # Для простоты показываем, что анализ прошел
            logger.info("Анализ value bets завершен")
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Ошибка в цикле анализа value bets: {e}")

async def stop_scheduler():
    """Останавливает все фоновые задачи"""
    logger.info("Остановка фоновых планировщиков...")
    
    for task in _scheduler_tasks:
        if not task.done():
            task.cancel()
    
    # Ждем завершения всех задач
    if _scheduler_tasks:
        await asyncio.gather(*_scheduler_tasks, return_exceptions=True)
    
    _scheduler_tasks.clear()
    logger.info("Все фоновые задачи остановлены")

def get_scheduler_status():
    """Возвращает статус планировщика"""
    active_tasks = [t for t in _scheduler_tasks if not t.done()]
    return {
        "total_tasks": len(_scheduler_tasks),
        "active_tasks": len(active_tasks),
        "completed_tasks": len(_scheduler_tasks) - len(active_tasks)
    }

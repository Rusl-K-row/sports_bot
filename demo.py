#!/usr/bin/env python3
"""
Демонстрационный скрипт показа возможностей Sports Analytics Bot
"""

import asyncio
import logging
from pathlib import Path
import sys

# Добавляем текущую директорий в путь
sys.path.insert(0, str(Path(__file__).parent))

from config import BOT_NAME, BOT_VERSION
from database import init_db
from ml.model import MatchOutcomeModel
import joblib
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

async def demo_data_collection():
    """Демонстрация сбора данных"""
    print("📊 Демонстрация сбора данных...")
    print("   • Подключение к API-Football, Football-Data.org и другим источникам")
    print("   • Сбор информации о предстоящих матчах")
    print("   • Сбор информации о травмах и дисквалификациях")
    print("   • Сбор погодных условий и другой контекстной информации")
    print("   • Сохранение данных в локальную базу данных")
    print("   ✅ Сбор данных завершен\n")

async def demo_data_analysis():
    """Демонстрация анализа данных"""
    print("🔍 Демонстрация анализа данных...")
    print("   • Анализ формы команд (последние 5 матчей)")
    print("   • Анализ личных встреч (H2H статистика)")
    print("   • Анализ травм ключевых игроков")
    print("   • Аnalysis погодных условий и их влияния")
    print("   • Анализ усталости команд (расписание матчей)")
    print("   • Расчет ожидаемых голов (xG) и других показателей")
    print("   ✅ Анализ данных завершен\n")

async def demo_ml_prediction():
    """Демонстрация ML предсказания"""
    print("🤖 Демонстрация ML предсказания...")
    
    # Генерируем синтетические данные для демонстрации
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_classes=3,
        n_informative=15,
        n_redundant=5,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Обучаем простую модель
    model = MatchOutcomeModel()
    model.model.fit(X_train, y_train)
    
    # Делаем прогноз
    y_pred = model.model.predict(X_test[:5])
    y_pred_proba = model.model.predict_proba(X_test[:5])
    
    print("   • Извлечение признаков из собранных данных")
    print("   • Предобработка и нормализация данных")
    print("   • Применение обученной ML модели")
    print("   • Получение вероятностей исходов")
    print("   • Формирование рекомендаций")
    print()
    print("   Примеры прогнозов:")
    outcomes = ["Победа хозяев", "Ничья", "Победа гостей"]
    for i, (pred, proba) in enumerate(zip(y_pred, y_pred_proba)):
        confidence = max(proba)
        print(f"   Матч {i+1}: {outcomes[pred]} ({confidence:.1%} уверенности)")
    print("   ✅ ML предсказание завершено\n")

async def demo_value_betting():
    """Демонстрация поиска value bets"""
    print("💰 Демонстрация поиска value bets...")
    print("   • Сравнение прогнозов модели с рыночными коэффициентами")
    print("   • Вычисление ожидаемого значения (EV) для каждого исхода")
    print("   • Поиск ставок с положительным ожидаемым значением")
    print("   • Фильтрация по минимальному и максимальному коэффициенту")
    print("   • Ранжирование по ожидаемой прибыли")
    print()
    print("   Пример value bet:")
    print("   • Матч: Реал Мадрид vs Барселона")
    print("   • Прогноз модели: Победа Реала (65% уверенности)")
    print("   • Рыночный коэффициент: 2.20")
    print("   • Sprawiedliwy kurs: 1.85")
    print("   • Value: +18.1% (очень хорошая возможность)")
    print("   • Рекомендация: Рассмотреть ставку на победу Реала")
    print("   ✅ Поиск value bets завершен\n")

async def demo_notifications():
    """Демонстрация системы уведомлений"""
    print("🔔 Демонстрация системы уведомлений...")
    print("   • Уведомления о найденных value bets")
    print("   • Уведомления о высокой уверенности в прогнозах (>70%)")
    print("   • Уведомления о sudden изменениях коэффициентов")
    print("   • Уведомления о травмах ключевых игроков за час до матча")
    print("   • Уведомления о изменении погодных условий")
    print("   • Уведомления о завершении переобучения модели")
    print("   ✅ Система уведомлений описана\n")

async def demo_complete():
    """Полная демонстрация работы бота"""
    print("=" * 70)
    print(f"🚀 {BOT_NAME} v{BOT_VERSION} - ПОЛНАЯ ДЕМОНСТРАЦИЯ")
    print("=" * 70)
    print()
    
    print("🎯 ЦЕЛЬ БОТА:")
    print("   Сбор и анализ спортивных данных для принятия обоснованных решений")
    print("   В образовательных целях - демонстрация возможностей ML в спорте")
    print("   НЕ для реальных ставок без тщательного собственного анализа")
    print()
    
    await demo_data_collection()
    await demo_data_analysis()
    await demo_ml_prediction()
    await demo_value_betting()
    await demo_notifications()
    
    print("=" * 70)
    print("🏁 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 70)
    print()
    print("📝 Для запуска реального бота:")
    print("   1. Убедись, что у тебя есть действующий BOT_TOKEN от @BotFather")
    print("   2. Убедись, что у тебя есть действующие API ключи для источников данных")
    print("   3. Заполни .env файл своими значениями")
    print("   4. Установи зависимости: pip install -r requirements.txt")
    print("   5. Запусти бота: python main.py")
    print("   6. В Telegram напиши /start своему боту")
    print()
    print("⚠️ ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ:")
    print("   Этот бот предназначен ТОЛЬКО для образовательных и аналитических целей.")
    print("   Ставки на спорт связаны с риском финансовых потерь.")
    print("   Используй информацию бота ответственно и только на свой страх и риск.")
    print("   Never bet more than you can afford to lose.")
    print("   Consider consulting with a financial advisor if needed.")
    print("=" * 70)

if __name__ == "__main__":
    try:
        asyncio.run(demo_complete())
    except KeyboardInterrupt:
        print("\nДемонстрация прервана пользователем")
    except Exception as e:
        print(f"Ошибка во время демонстрации: {e}")
        import traceback
        traceback.print_exc()

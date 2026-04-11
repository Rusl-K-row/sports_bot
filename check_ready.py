#!/usr/bin/env python3
"""
Скрипт проверки готовности проекта к запуску
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Проверяет, установлены ли все необходимые зависимости"""
    required_packages = [
        'aiogram',
        'httpx', 
        'aiosqlite',
        'python-dotenv',
        'scikit-learn',
        'pandas',
        'numpy',
        'joblib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Отсутствуют зависимости: {', '.join(missing_packages)}")
        print("   Установи их командой: pip install -r requirements.txt")
        return False
    else:
        print("✅ Все зависимости установлены")
        return True

def check_env_file():
    """Проверяет наличие и заполненность .env файла"""
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("❌ Файл .env не найден")
        print("   Скопируй .env.example в .env и заполни свои значения")
        return False
    
    # Проверяем наличие обязательных переменных
    required_vars = ["BOT_TOKEN"]
    missing_or_empty = []
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            
        for var in required_vars:
            # Проверяем, что переменная присутствует и не является примерным значением
            if f"{var}=" not in content:
                missing_or_empty.append(f"{var} (отсутствует)")
            elif f"{var}=your_" in content:
                missing_or_empty.append(f"{var} (нужно заполнить реальное значение)")
    except Exception as e:
        print(f"❌ Ошибка чтения .env файла: {e}")
        return False
    
    if missing_or_empty:
        print(f"⚠️ Следующие переменные нужно заполнить: {', '.join(missing_or_empty)}")
        return False
    else:
        print("✅ Файл .env найден и содержит необходимые значения")
        return True

def check_project_structure():
    """Проверяет структуру проекта"""
    required_dirs = [
        "data",
        "models", 
        "logs",
        "api_clients",
        "ml",
        "utils",
        "notifications"
    ]
    
    missing_dirs = []
    
    for dir_name in required_dirs:
        dir_path = Path(__file__).parent / dir_name
        if not dir_path.exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Отсутствуют директории: {', '.join(missing_dirs)}")
        return False
    else:
        print("✅ Структура проекта корректна")
        return True

def check_entry_point():
    """Проверяет наличие точки входа"""
    main_file = Path(__file__).parent / "main.py"
    if not main_file.exists():
        print("❌ Файл main.py не найден")
        return False
    else:
        print("✅ Точка входа (main.py) найдена")
        return True

def main():
    """Главная функция проверки"""
    print("🔍 ПРОВЕРКА ГОТОВНОСТИ SPORTS ANALYTICS BOT")
    print("=" * 50)
    
    checks = [
        ("Структура проекта", check_project_structure),
        ("Точка входа", check_entry_point),
        ("Зависимости", check_dependencies),
        ("Файл окружения", check_env_file)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
        print("   Проект готов к запуску:")
        print("   python main.py")
    else:
        print("❌ НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОШЛИ")
        print("   Исправь ошибки выше перед запуском")
    
    print("=" * 50)
    return len([c for c in checks if c[1]()]) == len(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

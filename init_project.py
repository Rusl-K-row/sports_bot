#!/usr/bin/env python3
"""
Скрипт инициализации проекта Sports Analytics Bot
Проверяет зависимости, создает необходимые структуры и запускает тесты
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"\n🔧 {description}")
    print(f"Выполняется: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Успешно: {description}")
        if result.stdout.strip():
            print(f"Вывод: {stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {description}")
        print(f"Код возврата: {e.returncode}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def check_python_version():
    """Проверяет версию Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minore < 8):
        print(f"❌ Требуется Python 3.8+, установлен {version.major}.{version.minor}")
        return False
    print(f"✅ Версия Python {version.major}.{version.minor} подходит")
    return True

def install_dependencies():
    """Устанавливает зависимости из requirements.txt"""
    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        print("❌ Файл requirements.txt не найден")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r {req_file}",
        "Установка зависимостей"
    )

def create_directories():
    """Создает необходимые директории"""
    base_dir = Path(__file__).parent
    directories = [
        base_dir / "data",
        base_dir / "models", 
        base_dir / "logs",
        base_dir / "data" / "matches",
        base_dir / "data" / "injuries",
        base_dir / "models" / "backups"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Создана директория: {directory}")
    
    return True

def check_env_file():
    """Проверяет наличие и правильность .env файла"""
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print(f"⚠️ Файл .env не найден. Скопируй .env.example в .env и заполни свои значения:")
            print(f"   cp {env_example} {env_file}")
            return False
        else:
            print("❌ Ни .env, ни .env.example не найдены")
            return False
    
    # Проверяем наличие обязательных переменных
    required_vars = ["BOT_TOKEN"]
    missing_vars = []
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=" in content and f"{var}=your_" in content:
                missing_vars.append(var)
    except Exception as e:
        print(f"❌ Ошибка чтения .env файла: {e}")
        return False
    
    if missing_vars:
        print(f"⚠️ Следующие переменные нужно заполнить в .env: {', '.join(missing_vars)}")
        print(f"   Отредактируй файл {env_file}")
        return False
    
    print("✅ .env файл найден и содержит необходимые переменные")
    return True

def run_basic_tests():
    """Запускает базовые тесты импорта"""
    print("\n🧪 Запуск базовых тестов...")
    
    # Тестируем импорт основных модулей
    try:
        import config
        print("✅ config.py импортирован успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта config.py: {e}")
        return False
    
    try:
        from database import init_db
        print("✅ database.py импортирован успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта database.py: {e}")
        return False
    
    try:
        from ml.model import MatchOutcomeModel
        print("✅ ml/model.py импортирован успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта ml/model.py: {e}")
        return False
    
    try:
        from bot import dp, bot
        print("✅ bot.py импортирован успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта bot.py: {e}")
        return False
    
    print("✅ Все основные модули импортированы успешно")
    return True

def main():
    """Главная функция инициализации"""
    print("=" * 60)
    print("🚀 ИНИЦИАЛИЗАЦИЯ SPORTS ANALYTICS BOT")
    print("=" * 60)
    
    # Проверяем версию Python
    if not check_python_version():
        return False
    
    # Проверяем .env файл
    if not check_env_file():
        print("\n📝 Сначала настройте .env файл, затем запустите скрипт снова")
        return False
    
    # Создаем директории
    if not create_directories():
        return False
    
    # Устанавливаем зависимости
    if not install_dependencies():
        return False
    
    # Запускаем базовые тесты
    if not run_basic_tests():
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 60)
    print("\n📝 Следующие шаги:")
    print("1. Убедись, что твой .env файл содержит правильные значения")
    print("2. Запусти бот: python main.py")
    print("3. В Telegram напиши /start своему боту")
    print("4. Наслаждайся анализом спортивных данных!")
    print("\n⚠️ ВАЖНО: Этот бот предназначен ТОЛЬКО для образовательных целей.")
    print("   Ставки на спорт связаны с риском финансовых потерь.")
    print("   Используй информацию ответственно.")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

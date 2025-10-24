import os
import sys
from typing import Optional

class SimpleConfig:
    """
    Упрощенная конфигурация без Pydantic
    """
    def __init__(self):
        self.bot_token = self._get_bot_token()
    
    def _get_bot_token(self) -> str:
        # Сначала пробуем получить из переменных окружения
        token = os.getenv('BOT_TOKEN')
        
        # Если не найдено, пробуем прочитать из файла .env
        if not token:
            try:
                with open('.env', 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key.strip() == 'BOT_TOKEN':
                                token = value.strip()
                                break
            except FileNotFoundError:
                print("❌ Файл .env не найден!")
                print("📝 Создайте файл .env в корне проекта с содержимым:")
                print("BOT_TOKEN=your_actual_bot_token_here")
        
        if not token:
            print("❌ Токен бота не найден!")
            print("📝 Создайте файл .env в корне проекта с содержимым:")
            print("BOT_TOKEN=your_actual_bot_token_here")
            print("")
            print("🔧 Альтернативно, установите переменную окружения:")
            print("set BOT_TOKEN=your_token (Windows)")
            print("export BOT_TOKEN=your_token (Linux/Mac)")
            sys.exit(1)
            
        # Удаляем кавычки если они есть
        token = token.strip('"').strip("'")
        
        return token
    
    def get_secret_value(self) -> str:
        return self.bot_token

# Глобальная конфигурация
try:
    config = SimpleConfig()
    print(f"✅ Конфигурация загружена успешно! Токен: {config.bot_token[:10]}...")
except Exception as e:
    print(f"❌ Ошибка загрузки конфигурации: {e}")
    config = None
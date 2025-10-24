import os

def create_env_file():
    """Создает файл .env с токеном бота"""
    
    print("🤖 Настройка Telegram бота")
    print("=" * 40)
    
    token = input("Введите токен вашего бота (получите у @BotFather): ").strip()
    
    if not token:
        print("❌ Токен не может быть пустым!")
        return
    
    # Создаем .env файл
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(f'BOT_TOKEN={token}\n')
    
    print("✅ Файл .env успешно создан!")
    print("📁 Теперь вы можете запустить бота: python main.py")

if __name__ == "__main__":
    create_env_file()
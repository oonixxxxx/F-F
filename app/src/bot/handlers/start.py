from aiogram import Router, types
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import datetime
import json
import os

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Выводим информацию о пользователе в терминал
    print_user_info(user_id, username, first_name, last_name)
    
    # Сохраняем в базу данных
    save_user_to_json(user_id, username, first_name, last_name)
    
    await message.answer(f"Привет, {first_name}! Я бот который поможет тебе расспределить твое время правильно")

def print_user_info(user_id, username, first_name, last_name):
    """Выводит подробную информацию о пользователе в терминал"""
    from datetime import datetime
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print("\n" + "🎯" + "="*48 + "🎯")
    print("           📱 НОВЫЙ ЗАПУСК БОТА")
    print("🎯" + "="*48 + "🎯")
    print(f"🆔 ID: {user_id}")
    print(f"👤 Username: @{username}" if username else "👤 Username: ❌ не указан")
    print(f"📛 Имя: {first_name}" if first_name else "📛 Имя: ❌ не указано")
    print(f"📖 Фамилия: {last_name}" if last_name else "📖 Фамилия: ❌ не указана")
    print(f"🕐 Время запуска: {current_time}")
    print("🎯" + "="*48 + "🎯")
    print("✅ Пользователь добавлен в базу данных")
    print("🎯" + "="*48 + "🎯\n")

def save_user_to_json(user_id, username, first_name, last_name):
    """Сохраняет пользователя в JSON файл"""
    data = {}
    
    # Читаем существующие данные
    if os.path.exists('users.json'):
        try:
            with open('users.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    
    # Добавляем/обновляем пользователя
    data[str(user_id)] = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'registration_date': datetime.datetime.now().isoformat()
    }
    
    # Сохраняем обратно
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Пользователь {user_id} сохранен в базу данных")

@router.message(F.text == '/start')
async def start_handler(message: Message):
    # Этот хендлер дублирует Command("start"), можно удалить
    await message.answer('Hello! Welcome to the bot! Send "add_task" to add a task.')
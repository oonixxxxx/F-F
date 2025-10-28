import os
import json
import datetime

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
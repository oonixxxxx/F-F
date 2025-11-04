import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Временные хранилища для активных сессий
user_task_lists: Dict[int, Dict] = {}
user_edit_data: Dict[int, Dict] = {}

# Файл для хранения данных
DATA_FILE = "user_tasks.json"

def load_data():
    """Загрузка данных из JSON файла"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {e}")
    return {}

def save_data():
    """Сохранение данных в JSON файл"""
    try:
        data_to_save = {
            'user_task_lists': user_task_lists,
            'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Ошибка сохранения данных: {e}")

def initialize_user_task_list(user_id: int, username: str = "User", first_name: str = "User", last_name: str = None) -> None:
    """Инициализация списка задач для пользователя"""
    user_task_lists[user_id] = {
        'tasks': [],
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'username': username,
        'first_name': first_name,
        'last_name': last_name
    }
    save_data()  # Сохраняем после инициализации

def create_task_data(text: str, time: Optional[str] = None) -> Dict[str, Any]:
    """Создание структуры данных задачи"""
    return {
        "text": text.strip(),
        "time": time,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "has_time": time is not None
    }

async def save_task_to_db(user_id: int, text: str, time_estimate: str = None):
    """Сохранение задачи (в JSON файл)"""
    # Просто сохраняем данные в JSON
    save_data()
    print(f"💾 Задача сохранена в JSON: user_id={user_id}, text='{text}', time='{time_estimate}'")

def user_has_active_list(user_id: int) -> bool:
    """Проверка наличия активного списка"""
    return user_id in user_task_lists and user_task_lists[user_id]['tasks']

def get_user_tasks(user_id: int) -> List[Dict]:
    """Получение задач пользователя"""
    if user_id in user_task_lists:
        return user_task_lists[user_id]['tasks']
    return []

def get_user_task_list(user_id: int):
    """Получение всего списка задач пользователя"""
    return user_task_lists.get(user_id)

def set_user_task_list(user_id: int, task_list: Dict):
    """Установка списка задач пользователя"""
    user_task_lists[user_id] = task_list
    save_data()

def get_user_edit_data(user_id: int):
    """Получение данных редактирования"""
    return user_edit_data.get(user_id)

def set_user_edit_data(user_id: int, data: Dict):
    """Установка данных редактирования"""
    user_edit_data[user_id] = data

def delete_user_edit_data(user_id: int):
    """Удаление данных редактирования"""
    if user_id in user_edit_data:
        del user_edit_data[user_id]

# Загружаем данные при импорте модуля
try:
    data = load_data()
    if 'user_task_lists' in data:
        user_task_lists.update(data['user_task_lists'])
        print("✅ Данные загружены из JSON файла")
except Exception as e:
    print(f"❌ Ошибка загрузки данных при старте: {e}")
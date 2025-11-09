import json
import os
from pathlib import Path

USERS_FILE = "users.json"

def load_users() -> dict:
    """Загружает пользователей из JSON-файла. Возвращает словарь."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users: dict):
    """Сохраняет словарь пользователей в JSON-файл."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)
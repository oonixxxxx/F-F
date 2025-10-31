from typing import Dict, List, Any

# Глобальные хранилища данных
user_task_lists: Dict[int, Dict[str, Any]] = {}
user_edit_data: Dict[int, Dict[str, Any]] = {}


def get_user_task_list(user_id: int) -> Dict[str, Any]:
    """Получить список задач пользователя"""
    return user_task_lists.get(user_id, {'tasks': [], 'created_at': ''})


def set_user_task_list(user_id: int, task_list: Dict[str, Any]) -> None:
    """Установить список задач пользователя"""
    user_task_lists[user_id] = task_list


def delete_user_task_list(user_id: int) -> None:
    """Удалить список задач пользователя"""
    if user_id in user_task_lists:
        del user_task_lists[user_id]


def get_user_edit_data(user_id: int) -> Dict[str, Any]:
    """Получить данные редактирования пользователя"""
    return user_edit_data.get(user_id, {})


def set_user_edit_data(user_id: int, edit_data: Dict[str, Any]) -> None:
    """Установить данные редактирования пользователя"""
    user_edit_data[user_id] = edit_data


def delete_user_edit_data(user_id: int) -> None:
    """Удалить данные редактирования пользователя"""
    if user_id in user_edit_data:
        del user_edit_data[user_id]


def user_has_active_list(user_id: int) -> bool:
    """Проверить, есть ли у пользователя активный список"""
    return user_id in user_task_lists and bool(user_task_lists[user_id].get('tasks'))


def get_user_tasks(user_id: int) -> List[Dict[str, Any]]:
    """Получить задачи пользователя"""
    return user_task_lists.get(user_id, {}).get('tasks', [])
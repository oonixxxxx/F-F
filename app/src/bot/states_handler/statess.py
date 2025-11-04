from aiogram.fsm.state import State, StatesGroup

class TaskListForm(StatesGroup):
    """Состояния для работы со списками задач"""
    adding_tasks = State()                    # Основное состояние добавления задач
    waiting_for_task_text = State()           # Ожидание текста задачи (для времени)
    waiting_for_task_time = State()           # Ожидание выбора времени из кнопок
    waiting_for_custom_time = State()         # Ожидание пользовательского времени
    editing_task = State()                    # Редактирование существующей задачи
    selecting_task_for_remove = State()       # Выбор задачи для удаления
    selecting_task_for_rename = State()       # Выбор задачи для переименования
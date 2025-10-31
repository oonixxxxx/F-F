from aiogram.fsm.state import State, StatesGroup

class TaskListForm(StatesGroup):
    adding_tasks = State()           # Простое добавление (оставить для обратной совместимости)
    waiting_for_tasks = State()      # Быстрый список
    editing_task = State()           # Редактирование
    waiting_for_task_text = State()  # Ожидание текста задачи (НОВОЕ)
    waiting_for_task_time = State()  # Ожидание времени задачи (НОВОЕ)
from aiogram.fsm.state import State, StatesGroup

class TaskListForm(StatesGroup):
    adding_tasks = State()
    waiting_for_tasks = State()
    editing_task = State()  # Добавьте эту строку
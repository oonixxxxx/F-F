from aiogram.fsm.state import State, StatesGroup

class TaskListForm(StatesGroup):
    waiting_for_tasks = State()
    adding_tasks = State()
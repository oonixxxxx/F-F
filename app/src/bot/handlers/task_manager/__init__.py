from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.src.bot.states_handler.statess import TaskListForm
from app.src.bot.handlers.task_manager.task_service import (
    add_simple_task,
    handle_task_text_input,
    handle_custom_time_input,
)
from app.src.bot.handlers.task_manager.task_handlers import (
    handle_inline_buttons,
    handle_task_selection,
    handle_confirm_delete_list
)

# Создаем роутер для task_manager
router = Router()

# Основной обработчик сообщений для добавления задач
@router.message(TaskListForm.adding_tasks)
async def process_task_input(message: Message, state: FSMContext):
    """Обработчик ввода обычных задач"""
    await add_simple_task(message, message.from_user.id)

# Обработчики для состояний времени
@router.message(TaskListForm.waiting_for_task_text)
async def process_task_text_input(message: Message, state: FSMContext):
    """Обработчик ввода текста задачи для добавления с временем"""
    await handle_task_text_input(message, state)

@router.message(TaskListForm.waiting_for_custom_time)
async def process_custom_time_input(message: Message, state: FSMContext):
    """Обработчик ввода пользовательского времени"""
    await handle_custom_time_input(message, state)

# Обработчики callback-запросов
@router.callback_query(F.data.in_([
    "finish_list", "clear_list", "show_list", "edit_list", 
    "delete_list", "back_to_main", "add_task", "remove_task", 
    "rename_task", "shuffle_tasks", "cancel_action", "back_to_edit",
    "add_task_with_time", "time_custom", "cancel_time_input"
]) | F.data.startswith("time_"))
async def process_inline_buttons(callback: CallbackQuery, state: FSMContext):
    """Обработчик inline-кнопок"""
    await handle_inline_buttons(callback, state)

@router.callback_query(F.data.startswith(("select_rename_", "select_remove_", "confirm_remove_")))
async def process_task_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора задач для редактирования/удаления"""
    await handle_task_selection(callback, state)

@router.callback_query(F.data == "confirm_delete")
async def process_confirm_delete(callback: CallbackQuery, state: FSMContext):
    """Обработчик подтверждения удаления всего списка"""
    await handle_confirm_delete_list(callback, state)

# Обработчик редактирования задачи
@router.message(TaskListForm.editing_task)
async def process_edit_task_input(message: Message, state: FSMContext):
    """Обработчик ввода нового текста для редактирования задачи"""
    from app.src.bot.handlers.task_manager.task_service import handle_edit_task_input
    await handle_edit_task_input(message, state)

__all__ = ['router']
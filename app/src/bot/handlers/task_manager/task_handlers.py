from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.src.bot.handlers.task_manager.task_service import (
    finish_task_list, clear_task_list, show_current_list,
    edit_list, delete_list, add_task_with_time_handler,
    handle_time_suggestion, time_custom_handler, cancel_time_input_handler,
    back_to_main_inline, add_task_inline, remove_task_inline,
    rename_task_inline, shuffle_tasks_inline, cancel_action_inline,
    handle_select_rename_task, handle_select_remove_task, handle_confirm_remove_task
)
from .task_storage import user_task_lists


async def handle_inline_buttons(callback: CallbackQuery, state: FSMContext):
    """Единая точка входа для обработки inline-кнопок"""
    user_id = callback.from_user.id
    action = callback.data
    
    await callback.answer()
    
    action_handlers = {
        "finish_list": finish_task_list,
        "clear_list": clear_task_list,
        "show_list": show_current_list,
        "edit_list": edit_list,
        "delete_list": delete_list,
        "back_to_main": back_to_main_inline,
        "add_task": add_task_inline,
        "remove_task": remove_task_inline,
        "rename_task": rename_task_inline,
        "shuffle_tasks": shuffle_tasks_inline,
        "cancel_action": cancel_action_inline,
        "back_to_edit": edit_list,
        "add_task_with_time": add_task_with_time_handler,
        "time_custom": time_custom_handler,
        "cancel_time_input": cancel_time_input_handler,
    }
    
    handler = action_handlers.get(action)
    if handler:
        # Все функции теперь принимают одинаковые аргументы
        await handler(callback, state)
    else:
        # Обработка callback-ов времени (15min, 30min, etc)
        if action.startswith("time_"):
            await handle_time_suggestion(callback, state)


async def handle_task_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора задач для редактирования/удаления"""
    user_id = callback.from_user.id
    data_parts = callback.data.split('_')
    action_type = data_parts[0]
    
    await callback.answer()
    
    if action_type == "select":
        task_action = data_parts[1]  # rename или remove
        task_index = int(data_parts[2])
        
        if task_action == "rename":
            await handle_select_rename_task(callback, task_index, state)
        elif task_action == "remove":
            await handle_select_remove_task(callback, task_index)
    
    elif action_type == "confirm" and data_parts[1] == "remove":
        task_index = int(data_parts[2])
        await handle_confirm_remove_task(callback, task_index)


async def handle_confirm_delete_list(callback: CallbackQuery, state: FSMContext):
    """Обработчик подтверждения удаления всего списка"""
    user_id = callback.from_user.id
    
    if user_id in user_task_lists:
        del user_task_lists[user_id]
        from .task_storage import save_data
        save_data()
    
    await callback.message.answer("🗑️ Весь список задач удален!")
    await state.clear()


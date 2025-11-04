from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.src.bot.states_handler.statess import TaskListForm
from app.src.bot.keyboards.keyboard_handler import (
    get_tasks_inline_keyboard, 
    get_tasks_selection_keyboard,
    get_confirm_inline_keyboard
)
from app.src.bot.handlers.task_manager.task_service import (
    finish_task_list, clear_task_list, show_current_list,
    edit_list, delete_list, add_task_with_time_handler,
    handle_time_suggestion, time_custom_handler, cancel_time_input_handler,
    back_to_main_inline, add_task_inline, remove_task_inline,
    rename_task_inline, shuffle_tasks_inline, cancel_action_inline
)
from .task_storage import user_task_lists, user_edit_data

router = Router()


@router.callback_query(F.data.in_([
    "finish_list", "clear_list", "show_list", "edit_list", 
    "delete_list", "back_to_main", "add_task", "remove_task", 
    "rename_task", "shuffle_tasks", "cancel_action", "back_to_edit",
    "add_task_with_time", "time_custom", "cancel_time_input"
]))
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
        await handler(callback, state)
    else:
        # ИСПРАВЛЕНИЕ: Обработка callback-ов времени (15min, 30min, etc)
        if action.startswith("time_"):
            await handle_time_suggestion(callback, state)


# ИСПРАВЛЕНИЕ: Добавляем отдельный обработчик для callback-ов времени
@router.callback_query(F.data.startswith("time_"))
async def handle_time_callbacks(callback: CallbackQuery, state: FSMContext):
    """Обработчик callback-ов времени"""
    await handle_time_suggestion(callback, state)


@router.callback_query(F.data.startswith(("select_rename_", "select_remove_", "confirm_remove_")))
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


@router.callback_query(F.data == "confirm_delete")
async def handle_confirm_delete_list(callback: CallbackQuery, state: FSMContext):
    """Обработчик подтверждения удаления всего списка"""
    user_id = callback.from_user.id
    
    if user_id in user_task_lists:
        del user_task_lists[user_id]
    
    await callback.message.answer("🗑️ Весь список задач удален!")
    await state.clear()


async def handle_select_rename_task(callback: CallbackQuery, task_index: int, state: FSMContext):
    """Обработчик выбора задачи для переименования"""
    user_id = callback.from_user.id
    
    if user_id not in user_task_lists:
        await callback.message.answer("❌ Список не найден")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    if task_index < 0 or task_index >= len(tasks):
        await callback.message.answer("❌ Неверный номер задачи")
        return
    
    # Сохраняем индекс задачи для редактирования
    user_edit_data[user_id] = {
        'action': 'renaming',
        'task_index': task_index,
        'old_task': tasks[task_index]['text']
    }
    
    await callback.message.answer(
        f"📝 Редактирование задачи №{task_index + 1}:\n"
        f"Текущий текст: {tasks[task_index]['text']}\n\n"
        "Введите новый текст задачи:"
    )
    
    await state.set_state(TaskListForm.editing_task)


async def handle_select_remove_task(callback: CallbackQuery, task_index: int):
    """Обработчик выбора задачи для удаления"""
    user_id = callback.from_user.id
    
    if user_id not in user_task_lists:
        await callback.message.answer("❌ Список не найден")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    if task_index < 0 or task_index >= len(tasks):
        await callback.message.answer("❌ Неверный номер задачи")
        return
    
    task_to_remove = tasks[task_index]
    
    # Создаем клавиатуру подтверждения для конкретной задачи
    confirm_keyboard = get_confirm_inline_keyboard(f"remove_{task_index}")
    
    await callback.message.answer(
        f"⚠️ Вы уверены, что хотите удалить задачу №{task_index + 1}?\n"
        f"📝 {task_to_remove['text']}",
        reply_markup=confirm_keyboard
    )


async def handle_confirm_remove_task(callback: CallbackQuery, task_index: int):
    """Обработчик подтверждения удаления задачи"""
    user_id = callback.from_user.id
    
    if user_id not in user_task_lists:
        await callback.message.answer("❌ Список не найден")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    if task_index < 0 or task_index >= len(tasks):
        await callback.message.answer("❌ Неверный номер задачи")
        return
    
    # Удаляем задачу
    removed_task = tasks.pop(task_index)
    
    # Выводим в терминал
    print(f"➖ Удалена задача #{task_index + 1}: '{removed_task['text']}' - {callback.from_user.full_name}")
    
    await callback.message.answer(
        f"✅ Задача №{task_index + 1} удалена!\n"
        f"📝 {removed_task['text']}\n\n"
        f"📊 Осталось задач: {len(tasks)}",
        reply_markup=get_tasks_inline_keyboard()
    )
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.src.bot.states_handler.statess import TaskListForm
from app.src.bot.keyboards.keyboard_handler import (
    get_tasks_inline_keyboard, 
    get_time_suggestion_keyboard,
    ReplyKeyboardMarkup
)

from .task_storage import (
    user_task_lists, 
    user_edit_data,
    get_user_task_list,
    set_user_task_list,
    get_user_edit_data,
    set_user_edit_data,
    delete_user_edit_data,
    user_has_active_list,
    get_user_tasks
)


def initialize_user_task_list(user_id: int) -> None:
    """Инициализация списка задач для пользователя"""
    user_task_lists[user_id] = {
        'tasks': [],
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def create_task_data(text: str, time: Optional[str] = None) -> Dict[str, Any]:
    """Создание структуры данных задачи"""
    return {
        "text": text.strip(),
        "time": time,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "has_time": time is not None
    }


async def add_simple_task(message: Message, user_id: int) -> None:
    """Добавление простой задачи (без времени)"""
    task_text = message.text.strip()
    task_data = create_task_data(task_text)
    
    user_task_lists[user_id]['tasks'].append(task_data)
    current_count = len(user_task_lists[user_id]['tasks'])
    
    print(f"➕ Добавлена задача #{current_count}: '{task_text}' - {message.from_user.full_name}")
    
    await message.answer(
        f"✅ Задача #{current_count} добавлена!\n\n"
        f"Продолжайте вводить задачи или используйте кнопки для управления",
        reply_markup=get_tasks_inline_keyboard()
    )


async def finish_task_list(callback: CallbackQuery, state: FSMContext) -> None:
    """Завершение списка задач"""
    user_id = callback.from_user.id
    
    if not user_has_active_list(user_id):
        await callback.message.answer("❌ Список пуст! Добавьте хотя бы одну задачу.")
        return
    
    tasks = get_user_tasks(user_id)
    
    # Логирование в консоль
    _log_final_task_list(user_id, callback.from_user.full_name, tasks)
    
    # Формирование сообщения для пользователя
    tasks_text = _format_final_task_list(tasks)
    
    await callback.message.answer(
        tasks_text,
        reply_markup=ReplyKeyboardMarkup(remove_keyboard=True)
    )
    
    # Очистка
    if user_id in user_task_lists:
        del user_task_lists[user_id]
    await state.clear()


def _log_final_task_list(user_id: int, username: str, tasks: List[Dict]) -> None:
    """Логирование финального списка задач"""
    tasks_with_time = sum(1 for task in tasks if task.get("has_time"))
    
    print("=" * 70)
    print("📋 ФИНАЛЬНЫЙ СПИСОК ЗАДАЧ")
    print("=" * 70)
    print(f"👤 Пользователь: {username} (ID: {user_id})")
    print(f"📊 Всего задач: {len(tasks)}")
    print(f"⏱️ Задач со временем: {tasks_with_time}")
    print("-" * 70)
    
    for i, task_data in enumerate(tasks, 1):
        task_text = task_data["text"]
        task_time = task_data.get("time")
        
        if task_time:
            print(f"{i:2d}. {task_text} [{task_time}]")
        else:
            print(f"{i:2d}. {task_text}")
    
    print("=" * 70)


def _format_final_task_list(tasks: List[Dict]) -> str:
    """Форматирование финального списка для пользователя"""
    tasks_text = "✅ Ваш список задач завершен!\n\n"
    tasks_with_time = 0
    
    for i, task_data in enumerate(tasks, 1):
        task_text = task_data["text"]
        task_time = task_data.get("time")
        
        if task_time:
            tasks_text += f"{i}. {task_text} ⏱️ {task_time}\n"
            tasks_with_time += 1
        else:
            tasks_text += f"{i}. {task_text}\n"
    
    tasks_text += f"\n📊 Всего задач: {len(tasks)}"
    
    if tasks_with_time > 0:
        tasks_text += f"\n⏱️ Задач со временем: {tasks_with_time}"
    
    return tasks_text


async def clear_task_list(callback: CallbackQuery, state: FSMContext) -> None:
    """Очистка списка задач"""
    user_id = callback.from_user.id
    if user_id in user_task_lists:
        user_task_lists[user_id]['tasks'] = []
    
    await callback.message.answer("📭 Список очищен. Начинаем заново!")
    print(f"🔄 Список очищен для пользователя {callback.from_user.full_name}")


async def show_current_list(callback: CallbackQuery) -> None:
    """Показать текущий список задач"""
    user_id = callback.from_user.id
    
    if not user_has_active_list(user_id):
        await callback.message.answer("📭 Список пока пуст")
        return
    
    tasks = get_user_tasks(user_id)
    tasks_text = "📋 Текущий список задач:\n\n"
    
    for i, task_data in enumerate(tasks, 1):
        task_text = task_data["text"]
        task_time = task_data.get("time")
        
        if task_time:
            tasks_text += f"{i}. {task_text} ⏱️ {task_time}\n"
        else:
            tasks_text += f"{i}. {task_text}\n"
    
    await callback.message.answer(tasks_text, reply_markup=get_tasks_inline_keyboard())


async def edit_list(callback: CallbackQuery) -> None:
    """Редактирование списка задач"""
    user_id = callback.from_user.id
    
    if not user_has_active_list(user_id):
        await callback.message.answer("📭 Список пуст! Нечего редактировать.")
        return
    
    from app.src.bot.keyboards.keyboard_handler import get_edit_inline_keyboard
    await callback.message.answer(
        "✏️ Редактирование списка задач:",
        reply_markup=get_edit_inline_keyboard()
    )


async def delete_list(callback: CallbackQuery, state: FSMContext) -> None:
    """Удаление списка задач"""
    user_id = callback.from_user.id
    
    if user_id not in user_task_lists:
        await callback.message.answer("❌ У вас нет активных списков для удаления")
        return
    
    from app.src.bot.keyboards.keyboard_handler import get_confirm_inline_keyboard
    await callback.message.answer(
        "⚠️ Вы уверены, что хотите удалить весь список задач?",
        reply_markup=get_confirm_inline_keyboard("delete")
    )


async def add_task_with_time_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Начало процесса добавления задачи с временем"""
    user_id = callback.from_user.id
    
    if not user_has_active_list(user_id):
        await callback.message.answer(
            "❌ У вас нет активного списка задач! Сначала создайте список через /add_tasks_list"
        )
        return
    
    # Сохраняем временные данные для этого процесса
    user_edit_data[user_id] = {
        'action': 'adding_task_with_time',
        'step': 'waiting_for_text'
    }
    
    # Просим ввести текст задачи
    await callback.message.answer(
        "📝 Введите текст задачи:\n\n"
        "Пример: 'Подготовить отчет по проекту' или 'Изучить новую технологию'"
    )
    
    # Устанавливаем состояние ожидания текста задачи
    await state.set_state(TaskListForm.waiting_for_task_text)


async def time_custom_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Пользователь хочет ввести своё время"""
    user_id = callback.from_user.id
    
    if user_id not in user_edit_data:
        await callback.message.answer("❌ Ошибка процесса. Начните заново.")
        await state.clear()
        return
    
    await callback.message.answer(
        "⏱️ Введите своё время для задачи:\n\n"
        "Примеры:\n"
        "• '30 минут'\n" 
        "• '2 часа'\n"
        "• '1 день'\n"
        "• '45 мин'\n"
        "• '3 часа 30 минут'"
    )


async def cancel_time_input_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Отмена процесса добавления задачи с временем"""
    user_id = callback.from_user.id
    
    # Очищаем временные данные
    if user_id in user_edit_data:
        del user_edit_data[user_id]
    
    await callback.message.answer(
        "❌ Добавление задачи отменено.",
        reply_markup=get_tasks_inline_keyboard()
    )
    
    await state.clear()


async def handle_time_suggestion(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка выбора времени из быстрых вариантов"""
    user_id = callback.from_user.id
    
    if user_id not in user_edit_data:
        await callback.message.answer("❌ Ошибка процесса. Начните заново.")
        await state.clear()
        return
    
    # Получаем выбранное время из callback data
    time_mapping = {
        "time_15min": "15 минут",
        "time_30min": "30 минут", 
        "time_1h": "1 час",
        "time_2h": "2 часа",
        "time_4h": "4 часа",
        "time_1d": "1 день"
    }
    
    selected_time = time_mapping.get(callback.data)
    
    if selected_time:
        await save_task_with_time(callback, state, selected_time)


async def save_task_with_time(update: Union[Message, CallbackQuery], state: FSMContext, task_time: str) -> None:
    """Сохранение задачи с временем в список пользователя"""
    if isinstance(update, CallbackQuery):
        user_id = update.from_user.id
        message = update.message
    else:
        user_id = update.from_user.id
        message = update
    
    if user_id not in user_edit_data or user_id not in user_task_lists:
        await message.answer("❌ Ошибка сохранения. Начните заново.")
        await state.clear()
        return
    
    # Получаем данные из временного хранилища
    task_text = user_edit_data[user_id].get('task_text')
    
    if not task_text:
        await message.answer("❌ Ошибка: текст задачи не найден.")
        await state.clear()
        return
    
    # Создаем структуру задачи с временем
    task_data = create_task_data(task_text, task_time)
    
    # Добавляем задачу в список пользователя
    user_task_lists[user_id]['tasks'].append(task_data)
    
    # Получаем общее количество задач
    total_tasks = len(user_task_lists[user_id]['tasks'])
    
    # Логируем в консоль
    print(f"➕ Добавлена задача с временем #{total_tasks}: '{task_text}' [{task_time}] - {message.from_user.full_name}")
    
    # Отправляем подтверждение пользователю
    await message.answer(
        f"✅ Задача добавлена!\n\n"
        f"📝 {task_text}\n"
        f"⏱️ Время: {task_time}\n"
        f"📊 Всего задач в списке: {total_tasks}\n\n"
        f"Можете добавить ещё задачи или использовать другие функции:",
        reply_markup=get_tasks_inline_keyboard()
    )
    
    # Очищаем временные данные
    if user_id in user_edit_data:
        del user_edit_data[user_id]
    
    # Возвращаемся в состояние добавления обычных задач для совместимости
    await state.set_state(TaskListForm.adding_tasks)


# Дополнительные функции для callback обработчиков
async def back_to_main_inline(callback: CallbackQuery) -> None:
    """Возврат к главному меню"""
    await callback.message.answer(
        "⚡ Быстрые действия:",
        reply_markup=get_tasks_inline_keyboard()
    )


async def add_task_inline(callback: CallbackQuery, state: FSMContext) -> None:
    """Добавление задачи через inline-кнопку"""
    await callback.message.answer("Введите новую задачу:")
    await state.set_state(TaskListForm.adding_tasks)


async def remove_task_inline(callback: CallbackQuery) -> None:
    """Удаление задачи через inline-кнопку"""
    user_id = callback.from_user.id
    
    if not user_has_active_list(user_id):
        await callback.message.answer("❌ Список пуст! Нечего удалять.")
        return
    
    tasks = get_user_tasks(user_id)
    from app.src.bot.keyboards.keyboard_handler import get_tasks_selection_keyboard
    await callback.message.answer(
        "➖ Выберите задачу для удаления:",
        reply_markup=get_tasks_selection_keyboard(tasks, "select_remove")
    )


async def rename_task_inline(callback: CallbackQuery, state: FSMContext) -> None:
    """Переименование задачи через inline-кнопку"""
    user_id = callback.from_user.id
    
    if not user_has_active_list(user_id):
        await callback.message.answer("❌ Список пуст! Нечего редактировать.")
        return
    
    tasks = get_user_tasks(user_id)
    from app.src.bot.keyboards.keyboard_handler import get_tasks_selection_keyboard
    await callback.message.answer(
        "📝 Выберите задачу для переименования:",
        reply_markup=get_tasks_selection_keyboard(tasks, "select_rename")
    )


async def shuffle_tasks_inline(callback: CallbackQuery) -> None:
    """Перемешивание задач через inline-кнопку"""
    user_id = callback.from_user.id
    
    if not user_has_active_list(user_id):
        await callback.message.answer("❌ Список пуст! Нечего перемешивать.")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    import random
    # Сохраняем старый порядок для логов
    old_order = tasks.copy()
    
    # Перемешиваем задачи
    random.shuffle(tasks)
    
    # Выводим в терминал
    print(f"🔄 Задачи перемешаны для пользователя {callback.from_user.full_name}")
    print("   Было:", [f"'{task['text']}'" for task in old_order])
    print("   Стало:", [f"'{task['text']}'" for task in tasks])
    
    # Формируем сообщение с новым порядком
    tasks_text = "🔄 Задачи перемешаны!\n\nНовый порядок:\n"
    for i, task in enumerate(tasks, 1):
        tasks_text += f"{i}. {task['text']}\n"
    
    await callback.message.answer(
        tasks_text,
        reply_markup=get_tasks_inline_keyboard()
    )


async def cancel_action_inline(callback: CallbackQuery) -> None:
    """Отмена действия"""
    await callback.message.answer("Действие отменено")
    await callback.message.answer(
        "⚡ Быстрые действия:",
        reply_markup=get_tasks_inline_keyboard()
    )
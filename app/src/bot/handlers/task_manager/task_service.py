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
    user_has_active_list,
    get_user_tasks,
    initialize_user_task_list,
    create_task_data,
    save_task_to_db
)


async def add_simple_task(message: Message, user_id: int) -> None:
    """Добавление простой задачи (без времени)"""
    task_text = message.text.strip()
    
    # Гарантируем, что список существует
    if not user_has_active_list(user_id):
        initialize_user_task_list(
            user_id=user_id,
            username=message.from_user.username or "User",
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
    
    task_data = create_task_data(task_text)
    
    user_task_lists[user_id]['tasks'].append(task_data)
    current_count = len(user_task_lists[user_id]['tasks'])
    
    # Сохраняем в JSON
    await save_task_to_db(user_id, task_text)
    
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
        from .task_storage import save_data
        save_data()
    
    await callback.message.answer("📭 Список очищен. Начинаем заново!")
    print(f"🔄 Список очищен для пользователя {callback.from_user.full_name}")


async def show_current_list(callback: CallbackQuery, state: FSMContext = None) -> None:
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


async def edit_list(callback: CallbackQuery, state: FSMContext = None) -> None:
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


async def delete_list(callback: CallbackQuery, state: FSMContext = None) -> None:
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


# =============================================================================
# ФУНКЦИИ ДЛЯ РАБОТЫ СО ВРЕМЕНЕМ
# =============================================================================

async def add_task_with_time_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Начало процесса добавления задачи с временем"""
    user_id = callback.from_user.id
    
    # АВТОМАТИЧЕСКИ СОЗДАЕМ СПИСОК ЕСЛИ ЕГО НЕТ
    if not user_has_active_list(user_id):
        initialize_user_task_list(
            user_id=user_id,
            username=callback.from_user.username or "User",
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name
        )
        print(f"📝 Автоматически создан список для пользователя {callback.from_user.full_name}")
    
    # Сохраняем временные данные для этого процесса
    user_edit_data[user_id] = {
        'action': 'adding_task_with_time',
        'step': 'waiting_for_text'
    }
    
    # Просим ввести текст задачи
    await callback.message.answer(
        "📝 Введите текст задачи:\n\n"
        "Пример: 'Подготовить отчет по проекту' или 'Изучить новую технологию'\n\n"
        "После ввода текста вы сможете выбрать время выполнения."
    )
    
    # Устанавливаем состояние ожидания текста задачи
    await state.set_state(TaskListForm.waiting_for_task_text)


async def handle_task_text_input(message: Message, state: FSMContext) -> None:
    """Обработчик ввода текста задачи для добавления с временем"""
    user_id = message.from_user.id
    
    if user_id not in user_edit_data:
        await message.answer("❌ Процесс добавления прерван. Начните заново.")
        await state.clear()
        return
    
    task_text = message.text.strip()
    
    if not task_text:
        await message.answer("❌ Текст задачи не может быть пустым. Введите текст:")
        return
    
    # Сохраняем текст задачи во временное хранилище
    user_edit_data[user_id]['task_text'] = task_text
    user_edit_data[user_id]['step'] = 'waiting_for_time'
    
    # Показываем клавиатуру с выбором времени
    await message.answer(
        f"📝 Задача: {task_text}\n\n"
        "⏱️ Выберите время выполнения или введите своё:",
        reply_markup=get_time_suggestion_keyboard()
    )
    
    # Устанавливаем состояние ожидания выбора времени
    await state.set_state(TaskListForm.waiting_for_task_time)


async def time_custom_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Пользователь хочет ввести своё время"""
    user_id = callback.from_user.id
    
    if user_id not in user_edit_data:
        await callback.message.answer("❌ Процесс прерван. Начните добавление задачи заново через '⏱️ Добавить с временем'")
        await state.clear()
        return
    
    await callback.message.answer(
        "⏱️ Введите своё время для задачи:\n\n"
        "Примеры:\n"
        "• '30 минут'\n" 
        "• '2 часа'\n"
        "• '1 день'\n"
        "• '45 мин'\n"
        "• '3 часа 30 минут'\n\n"
        "Просто напишите время в ответном сообщении:"
    )
    
    # Устанавливаем состояние для ввода пользовательского времени
    await state.set_state(TaskListForm.waiting_for_custom_time)


async def handle_custom_time_input(message: Message, state: FSMContext) -> None:
    """Обработчик ввода пользовательского времени"""
    user_id = message.from_user.id
    
    if user_id not in user_edit_data:
        await message.answer("❌ Процесс добавления прерван. Начните заново.")
        await state.clear()
        return
    
    custom_time = message.text.strip()
    
    if not custom_time:
        await message.answer("❌ Время не может быть пустым. Введите время:")
        return
    
    # Сохраняем задачу с пользовательским временем
    await save_task_with_time(message, state, custom_time)


async def handle_time_suggestion(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка выбора времени из быстрых вариантов"""
    user_id = callback.from_user.id
    
    if user_id not in user_edit_data:
        await callback.message.answer("❌ Процесс прерван. Начните добавление задачи заново.")
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
    else:
        await callback.message.answer("❌ Неизвестное время. Попробуйте еще раз.")


async def save_task_with_time(update: Union[Message, CallbackQuery], state: FSMContext, task_time: str) -> None:
    """Сохранение задачи с временем в список пользователя"""
    if isinstance(update, CallbackQuery):
        user_id = update.from_user.id
        message = update.message
    else:
        user_id = update.from_user.id
        message = update
    
    # ГИБКАЯ ПРОВЕРКА - пытаемся восстановить процесс
    task_text = None
    if user_id in user_edit_data:
        task_text = user_edit_data[user_id].get('task_text')
    
    if not task_text:
        await message.answer("❌ Ошибка: текст задачи не найден. Начните заново.")
        await state.clear()
        return
    
    # ГАРАНТИРУЕМ, что список существует
    if not user_has_active_list(user_id):
        initialize_user_task_list(
            user_id=user_id,
            username=message.from_user.username or "User",
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
    
    # Создаем структуру задачи с временем
    task_data = create_task_data(task_text, task_time)
    
    # Добавляем задачу в список пользователя
    user_task_lists[user_id]['tasks'].append(task_data)
    
    # Сохраняем в JSON
    await save_task_to_db(user_id, task_text, task_time)
    
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
    
    # Возвращаемся в состояние добавления обычных задач
    await state.set_state(TaskListForm.adding_tasks)


async def cancel_time_input_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """Отмена процесса добавления задачи с временем"""
    user_id = callback.from_user.id
    
    # Очищаем временные данные
    if user_id in user_edit_data:
        del user_edit_data[user_id]
    
    await callback.message.answer(
        "❌ Добавление задачи с временем отменено.",
        reply_markup=get_tasks_inline_keyboard()
    )
    
    await state.clear()


# =============================================================================
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ CALLBACK ОБРАБОТЧИКОВ
# =============================================================================

async def back_to_main_inline(callback: CallbackQuery, state: FSMContext = None) -> None:
    """Возврат к главному меню"""
    await callback.message.answer(
        "⚡ Быстрые действия:",
        reply_markup=get_tasks_inline_keyboard()
    )


async def add_task_inline(callback: CallbackQuery, state: FSMContext) -> None:
    """Добавление задачи через inline-кнопку"""
    # Гарантируем, что список существует
    if not user_has_active_list(callback.from_user.id):
        initialize_user_task_list(
            user_id=callback.from_user.id,
            username=callback.from_user.username or "User",
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name
        )
    
    await callback.message.answer("Введите новую задачу:")
    await state.set_state(TaskListForm.adding_tasks)


async def remove_task_inline(callback: CallbackQuery, state: FSMContext = None) -> None:
    """Удаление задачи через inline-кнопку"""
    user_id = callback.from_user.id
    
    if not user_has_active_list(user_id):
        await callback.message.answer("❌ Список пуст! Нечего удалять.")
        return
    
    tasks = get_user_tasks(user_id)
    from app.src.bot.keyboards.keyboard_handler import get_tasks_selection_keyboard
    await callback.message.answer(
        "➖ Выберите задачу для удаления:",
        reply_markup=get_tasks_selection_keyboard(tasks, "remove")
    )


async def rename_task_inline(callback: CallbackQuery, state: FSMContext = None) -> None:
    """Переименование задачи через inline-кнопку"""
    user_id = callback.from_user.id
    
    if not user_has_active_list(user_id):
        await callback.message.answer("❌ Список пуст! Нечего редактировать.")
        return
    
    tasks = get_user_tasks(user_id)
    from app.src.bot.keyboards.keyboard_handler import get_tasks_selection_keyboard
    await callback.message.answer(
        "📝 Выберите задачу для переименования:",
        reply_markup=get_tasks_selection_keyboard(tasks, "rename")
    )


async def shuffle_tasks_inline(callback: CallbackQuery, state: FSMContext = None) -> None:
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


async def cancel_action_inline(callback: CallbackQuery, state: FSMContext = None) -> None:
    """Отмена действия"""
    await callback.message.answer("Действие отменено")
    await callback.message.answer(
        "⚡ Быстрые действия:",
        reply_markup=get_tasks_inline_keyboard()
    )


# =============================================================================
# ФУНКЦИИ ДЛЯ ОБРАБОТКИ ВЫБОРА ЗАДАЧ
# =============================================================================

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
    from app.src.bot.keyboards.keyboard_handler import get_confirm_inline_keyboard
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
    
    # Сохраняем изменения
    from .task_storage import save_data
    save_data()
    
    # Выводим в терминал
    print(f"➖ Удалена задача #{task_index + 1}: '{removed_task['text']}' - {callback.from_user.full_name}")
    
    await callback.message.answer(
        f"✅ Задача №{task_index + 1} удалена!\n"
        f"📝 {removed_task['text']}\n\n"
        f"📊 Осталось задач: {len(tasks)}",
        reply_markup=get_tasks_inline_keyboard()
    )

async def handle_edit_task_input(message: Message, state: FSMContext):
    """Обработчик ввода нового текста для редактирования задачи"""
    user_id = message.from_user.id
    
    if user_id not in user_edit_data:
        await message.answer("❌ Процесс редактирования прерван. Начните заново.")
        await state.clear()
        return
    
    edit_data = user_edit_data[user_id]
    if edit_data['action'] != 'renaming':
        await message.answer("❌ Неизвестное действие.")
        await state.clear()
        return
    
    new_text = message.text.strip()
    if not new_text:
        await message.answer("❌ Текст задачи не может быть пустым. Введите новый текст:")
        return
    
    task_index = edit_data['task_index']
    
    if user_id not in user_task_lists:
        await message.answer("❌ Список задач не найден.")
        await state.clear()
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    if task_index < 0 or task_index >= len(tasks):
        await message.answer("❌ Неверный номер задачи.")
        await state.clear()
        return
    
    # Сохраняем старый текст для логов
    old_text = tasks[task_index]['text']
    
    # Обновляем задачу
    tasks[task_index]['text'] = new_text
    tasks[task_index]['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Сохраняем изменения
    from .task_storage import save_data
    save_data()
    
    # Логируем
    print(f"✏️ Задача #{task_index + 1} переименована: '{old_text}' -> '{new_text}' - {message.from_user.full_name}")
    
    # Очищаем временные данные
    del user_edit_data[user_id]
    
    await message.answer(
        f"✅ Задача №{task_index + 1} переименована!\n\n"
        f"📝 Было: {old_text}\n"
        f"📝 Стало: {new_text}",
        reply_markup=get_tasks_inline_keyboard()
    )
    
    await state.clear()
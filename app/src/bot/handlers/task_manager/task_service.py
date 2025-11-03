# Импорты необходимых модулей и классов
from datetime import datetime  # Для работы с датой и временем
from typing import Dict, List, Any, Optional, Union  # Аннотации типов для лучшей читаемости кода
from aiogram.types import Message, CallbackQuery  # Типы сообщений и callback-запросов
from aiogram.fsm.context import FSMContext  # Контекст машины состояний

# Импорт состояний бота из модуля состояний
from app.src.bot.states_handler.statess import TaskListForm

# Импорт функций для создания клавиатур
from app.src.bot.keyboards.keyboard_handler import (
    get_tasks_inline_keyboard,  # Клавиатура для управления задачами
    get_time_suggestion_keyboard,  # Клавиатура с предложениями времени
    ReplyKeyboardMarkup  # Класс для создания reply-клавиатур
)

# Импорт функций для работы с хранилищами данных пользователей
from .task_storage import (
    user_task_lists,  # Глобальное хранилище списков задач пользователей
    user_edit_data,  # Глобальное хранилище временных данных редактирования
    get_user_task_list,  # Функция получения списка задач пользователя
    set_user_task_list,  # Функция установки списка задач пользователя
    get_user_edit_data,  # Функция получения данных редактирования
    set_user_edit_data,  # Функция установки данных редактирования
    delete_user_edit_data,  # Функция удаления данных редактирования
    user_has_active_list,  # Функция проверки наличия активного списка
    get_user_tasks  # Функция получения задач пользователя
)


def initialize_user_task_list(user_id: int) -> None:
    """
    Инициализация списка задач для пользователя
    
    Args:
        user_id (int): ID пользователя Telegram
    """
    # Создаем структуру данных для хранения списка задач пользователя
    user_task_lists[user_id] = {
        'tasks': [],  # Пустой список задач
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Время создания списка
    }


def create_task_data(text: str, time: Optional[str] = None) -> Dict[str, Any]:
    """
    Создание структуры данных задачи
    
    Args:
        text (str): Текст задачи
        time (Optional[str]): Время для выполнения (опционально)
    
    Returns:
        Dict[str, Any]: Структура данных задачи
    """
    return {
        "text": text.strip(),  # Текст задачи (убираем лишние пробелы)
        "time": time,  # Время выполнения (может быть None)
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Время создания задачи
        "has_time": time is not None  # Флаг наличия времени
    }


async def add_simple_task(message: Message, user_id: int) -> None:
    """
    Добавление простой задачи (без времени)
    
    Args:
        message (Message): Объект сообщения от пользователя
        user_id (int): ID пользователя
    """
    # Извлекаем и очищаем текст задачи из сообщения
    task_text = message.text.strip()
    # Создаем структуру данных задачи
    task_data = create_task_data(task_text)
    
    # Добавляем задачу в список пользователя
    user_task_lists[user_id]['tasks'].append(task_data)
    # Получаем текущее количество задач
    current_count = len(user_task_lists[user_id]['tasks'])
    
    # Логируем добавление задачи в консоль
    print(f"➕ Добавлена задача #{current_count}: '{task_text}' - {message.from_user.full_name}")
    
    # Отправляем подтверждение пользователю
    await message.answer(
        f"✅ Задача #{current_count} добавлена!\n\n"
        f"Продолжайте вводить задачи или используйте кнопки для управления",
        reply_markup=get_tasks_inline_keyboard()  # Показываем клавиатуру управления
    )


async def finish_task_list(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Завершение списка задач - финальный вывод и очистка
    
    Args:
        callback (CallbackQuery): Callback от кнопки завершения
        state (FSMContext): Контекст машины состояний
    """
    user_id = callback.from_user.id
    
    # Проверяем наличие активного списка задач
    if not user_has_active_list(user_id):
        await callback.message.answer("❌ Список пуст! Добавьте хотя бы одну задачу.")
        return
    
    # Получаем список задач пользователя
    tasks = get_user_tasks(user_id)
    
    # Логирование финального списка в консоль
    _log_final_task_list(user_id, callback.from_user.full_name, tasks)
    
    # Форматируем список задач для отправки пользователю
    tasks_text = _format_final_task_list(tasks)
    
    # Отправляем финальный список пользователю
    await callback.message.answer(
        tasks_text,
        reply_markup=ReplyKeyboardMarkup(remove_keyboard=True)  # Убираем клавиатуру
    )
    
    # Очищаем данные пользователя
    if user_id in user_task_lists:
        del user_task_lists[user_id]  # Удаляем список задач
    await state.clear()  # Очищаем состояние машины состояний


def _log_final_task_list(user_id: int, username: str, tasks: List[Dict]) -> None:
    """
    Логирование финального списка задач в консоль
    
    Args:
        user_id (int): ID пользователя
        username (str): Имя пользователя
        tasks (List[Dict]): Список задач
    """
    # Подсчитываем количество задач со временем
    tasks_with_time = sum(1 for task in tasks if task.get("has_time"))
    
    # Форматированный вывод в консоль
    print("=" * 70)
    print("📋 ФИНАЛЬНЫЙ СПИСОК ЗАДАЧ")
    print("=" * 70)
    print(f"👤 Пользователь: {username} (ID: {user_id})")
    print(f"📊 Всего задач: {len(tasks)}")
    print(f"⏱️ Задач со временем: {tasks_with_time}")
    print("-" * 70)
    
    # Выводим каждую задачу с номером
    for i, task_data in enumerate(tasks, 1):
        task_text = task_data["text"]
        task_time = task_data.get("time")
        
        if task_time:
            print(f"{i:2d}. {task_text} [{task_time}]")  # Задача со временем
        else:
            print(f"{i:2d}. {task_text}")  # Задача без времени
    
    print("=" * 70)


def _format_final_task_list(tasks: List[Dict]) -> str:
    """
    Форматирование финального списка для отправки пользователю
    
    Args:
        tasks (List[Dict]): Список задач
    
    Returns:
        str: Отформатированный текст списка задач
    """
    tasks_text = "✅ Ваш список задач завершен!\n\n"
    tasks_with_time = 0
    
    # Формируем текст с нумерованным списком задач
    for i, task_data in enumerate(tasks, 1):
        task_text = task_data["text"]
        task_time = task_data.get("time")
        
        if task_time:
            tasks_text += f"{i}. {task_text} ⏱️ {task_time}\n"
            tasks_with_time += 1
        else:
            tasks_text += f"{i}. {task_text}\n"
    
    # Добавляем статистику
    tasks_text += f"\n📊 Всего задач: {len(tasks)}"
    
    if tasks_with_time > 0:
        tasks_text += f"\n⏱️ Задач со временем: {tasks_with_time}"
    
    return tasks_text


async def clear_task_list(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Очистка списка задач (без удаления самого списка)
    
    Args:
        callback (CallbackQuery): Callback от кнопки очистки
        state (FSMContext): Контекст машины состояний
    """
    user_id = callback.from_user.id
    # Очищаем список задач, но сохраняем структуру списка
    if user_id in user_task_lists:
        user_task_lists[user_id]['tasks'] = []
    
    await callback.message.answer("📭 Список очищен. Начинаем заново!")
    # Логируем действие очистки
    print(f"🔄 Список очищен для пользователя {callback.from_user.full_name}")


async def show_current_list(callback: CallbackQuery) -> None:
    """
    Показать текущий список задач
    
    Args:
        callback (CallbackQuery): Callback от кнопки показа
    """
    user_id = callback.from_user.id
    
    # Проверяем наличие активного списка
    if not user_has_active_list(user_id):
        await callback.message.answer("📭 Список пока пуст")
        return
    
    # Получаем задачи пользователя
    tasks = get_user_tasks(user_id)
    tasks_text = "📋 Текущий список задач:\n\n"
    
    # Формируем текст с текущими задачами
    for i, task_data in enumerate(tasks, 1):
        task_text = task_data["text"]
        task_time = task_data.get("time")
        
        if task_time:
            tasks_text += f"{i}. {task_text} ⏱️ {task_time}\n"
        else:
            tasks_text += f"{i}. {task_text}\n"
    
    # Отправляем список с клавиатурой управления
    await callback.message.answer(tasks_text, reply_markup=get_tasks_inline_keyboard())


async def edit_list(callback: CallbackQuery) -> None:
    """
    Редактирование списка задач - переход в режим редактирования
    
    Args:
        callback (CallbackQuery): Callback от кнопки редактирования
    """
    user_id = callback.from_user.id
    
    # Проверяем наличие списка для редактирования
    if not user_has_active_list(user_id):
        await callback.message.answer("📭 Список пуст! Нечего редактировать.")
        return
    
    # Импортируем клавиатуру редактирования (импорт внутри функции для избежания циклических импортов)
    from app.src.bot.keyboards.keyboard_handler import get_edit_inline_keyboard
    await callback.message.answer(
        "✏️ Редактирование списка задач:",
        reply_markup=get_edit_inline_keyboard()  # Показываем клавиатуру редактирования
    )


async def delete_list(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Удаление списка задач - запрос подтверждения
    
    Args:
        callback (CallbackQuery): Callback от кнопки удаления
        state (FSMContext): Контекст машины состояний
    """
    user_id = callback.from_user.id
    
    # Проверяем наличие списка для удаления
    if user_id not in user_task_lists:
        await callback.message.answer("❌ У вас нет активных списков для удаления")
        return
    
    # Импортируем клавиатуру подтверждения
    from app.src.bot.keyboards.keyboard_handler import get_confirm_inline_keyboard
    await callback.message.answer(
        "⚠️ Вы уверены, что хотите удалить весь список задач?",
        reply_markup=get_confirm_inline_keyboard("delete")  # Клавиатура с подтверждением удаления
    )


async def add_task_with_time_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Начало процесса добавления задачи с временем
    
    Args:
        callback (CallbackQuery): Callback от кнопки добавления с временем
        state (FSMContext): Контекст машины состояний
    """
    user_id = callback.from_user.id
    
    # Проверяем наличие активного списка
    if not user_has_active_list(user_id):
        await callback.message.answer(
            "❌ У вас нет активного списка задач! Сначала создайте список через /add_tasks_list"
        )
        return
    
    # Сохраняем временные данные для этого процесса
    user_edit_data[user_id] = {
        'action': 'adding_task_with_time',  # Тип действия
        'step': 'waiting_for_text'  # Текущий шаг процесса
    }
    
    # Просим пользователя ввести текст задачи
    await callback.message.answer(
        "📝 Введите текст задачи:\n\n"
        "Пример: 'Подготовить отчет по проекту' или 'Изучить новую технологию'"
    )
    
    # Устанавливаем состояние ожидания текста задачи
    await state.set_state(TaskListForm.waiting_for_task_text)


async def time_custom_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора пользовательского времени
    
    Args:
        callback (CallbackQuery): Callback от кнопки своего времени
        state (FSMContext): Контекст машины состояний
    """
    user_id = callback.from_user.id
    
    # Проверяем наличие активного процесса добавления
    if user_id not in user_edit_data:
        await callback.message.answer("❌ Ошибка процесса. Начните заново.")
        await state.clear()
        return
    
    # Запрашиваем у пользователя ввод своего времени
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
    """
    Отмена процесса добавления задачи с временем
    
    Args:
        callback (CallbackQuery): Callback от кнопки отмены
        state (FSMContext): Контекст машины состояний
    """
    user_id = callback.from_user.id
    
    # Очищаем временные данные процесса
    if user_id in user_edit_data:
        del user_edit_data[user_id]
    
    # Уведомляем пользователя и показываем основную клавиатуру
    await callback.message.answer(
        "❌ Добавление задачи отменено.",
        reply_markup=get_tasks_inline_keyboard()
    )
    
    # Очищаем состояние
    await state.clear()


async def handle_time_suggestion(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка выбора времени из быстрых вариантов
    
    Args:
        callback (CallbackQuery): Callback от кнопки быстрого времени
        state (FSMContext): Контекст машины состояний
    """
    user_id = callback.from_user.id
    
    # Проверяем наличие активного процесса
    if user_id not in user_edit_data:
        await callback.message.answer("❌ Ошибка процесса. Начните заново.")
        await state.clear()
        return
    
    # Сопоставление callback_data с человеко-читаемым временем
    time_mapping = {
        "time_15min": "15 минут",
        "time_30min": "30 минут", 
        "time_1h": "1 час",
        "time_2h": "2 часа",
        "time_4h": "4 часа",
        "time_1d": "1 день"
    }
    
    # Получаем выбранное время
    selected_time = time_mapping.get(callback.data)
    
    if selected_time:
        # Сохраняем задачу с выбранным временем
        await save_task_with_time(callback, state, selected_time)


async def save_task_with_time(update: Union[Message, CallbackQuery], state: FSMContext, task_time: str) -> None:
    """
    Сохранение задачи с временем в список пользователя
    
    Args:
        update (Union[Message, CallbackQuery]): Объект обновления (сообщение или callback)
        state (FSMContext): Контекст машины состояний
        task_time (str): Время для задачи
    """
    # Определяем тип обновления и извлекаем данные
    if isinstance(update, CallbackQuery):
        user_id = update.from_user.id
        message = update.message
    else:
        user_id = update.from_user.id
        message = update
    
    # Проверяем наличие необходимых данных
    if user_id not in user_edit_data or user_id not in user_task_lists:
        await message.answer("❌ Ошибка сохранения. Начните заново.")
        await state.clear()
        return
    
    # Получаем текст задачи из временного хранилища
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
    
    # Логируем добавление в консоль
    print(f"➕ Добавлена задача с временем #{total_tasks}: '{task_text}' [{task_time}] - {message.from_user.full_name}")
    
    # Отправляем подтверждение пользователю
    await message.answer(
        f"✅ Задача добавлена!\n\n"
        f"📝 {task_text}\n"
        f"⏱️ Время: {task_time}\n"
        f"📊 Всего задач в списке: {total_tasks}\n\n"
        f"Можете добавить ещё задачи или использовать другие функции:",
        reply_markup=get_tasks_inline_keyboard()  # Возвращаем основную клавиатуру
    )
    
    # Очищаем временные данные процесса
    if user_id in user_edit_data:
        del user_edit_data[user_id]
    
    # Возвращаемся в состояние добавления обычных задач для совместимости
    await state.set_state(TaskListForm.adding_tasks)


# Дополнительные функции для callback обработчиков

async def back_to_main_inline(callback: CallbackQuery) -> None:
    """
    Возврат к главному меню управления задачами
    
    Args:
        callback (CallbackQuery): Callback от кнопки возврата
    """
    await callback.message.answer(
        "⚡ Быстрые действия:",
        reply_markup=get_tasks_inline_keyboard()  # Показываем основную клавиатуру
    )


async def add_task_inline(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Добавление задачи через inline-кнопку
    
    Args:
        callback (CallbackQuery): Callback от кнопки добавления
        state (FSMContext): Контекст машины состояний
    """
    await callback.message.answer("Введите новую задачу:")
    # Устанавливаем состояние добавления задач
    await state.set_state(TaskListForm.adding_tasks)


async def remove_task_inline(callback: CallbackQuery) -> None:
    """
    Удаление задачи через inline-кнопку
    
    Args:
        callback (CallbackQuery): Callback от кнопки удаления
    """
    user_id = callback.from_user.id
    
    # Проверяем наличие задач для удаления
    if not user_has_active_list(user_id):
        await callback.message.answer("❌ Список пуст! Нечего удалять.")
        return
    
    # Получаем список задач
    tasks = get_user_tasks(user_id)
    # Импортируем клавиатуру выбора задач
    from app.src.bot.keyboards.keyboard_handler import get_tasks_selection_keyboard
    await callback.message.answer(
        "➖ Выберите задачу для удаления:",
        reply_markup=get_tasks_selection_keyboard(tasks, "select_remove")  # Клавиатура для выбора удаления
    )


async def rename_task_inline(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Переименование задачи через inline-кнопку
    
    Args:
        callback (CallbackQuery): Callback от кнопки переименования
        state (FSMContext): Контекст машины состояний
    """
    user_id = callback.from_user.id
    
    # Проверяем наличие задач для редактирования
    if not user_has_active_list(user_id):
        await callback.message.answer("❌ Список пуст! Нечего редактировать.")
        return
    
    # Получаем список задач
    tasks = get_user_tasks(user_id)
    # Импортируем клавиатуру выбора задач
    from app.src.bot.keyboards.keyboard_handler import get_tasks_selection_keyboard
    await callback.message.answer(
        "📝 Выберите задачу для переименования:",
        reply_markup=get_tasks_selection_keyboard(tasks, "select_rename")  # Клавиатура для выбора переименования
    )


async def shuffle_tasks_inline(callback: CallbackQuery) -> None:
    """
    Перемешивание задач через inline-кнопку
    
    Args:
        callback (CallbackQuery): Callback от кнопки перемешивания
    """
    user_id = callback.from_user.id
    
    # Проверяем наличие задач для перемешивания
    if not user_has_active_list(user_id):
        await callback.message.answer("❌ Список пуст! Нечего перемешивать.")
        return
    
    # Получаем задачи пользователя
    tasks = user_task_lists[user_id]['tasks']
    
    import random
    # Сохраняем старый порядок для логов
    old_order = tasks.copy()
    
    # Перемешиваем задачи (in-place)
    random.shuffle(tasks)
    
    # Логируем перемешивание в консоль
    print(f"🔄 Задачи перемешаны для пользователя {callback.from_user.full_name}")
    print("   Было:", [f"'{task['text']}'" for task in old_order])
    print("   Стало:", [f"'{task['text']}'" for task in tasks])
    
    # Формируем сообщение с новым порядком
    tasks_text = "🔄 Задачи перемешаны!\n\nНовый порядок:\n"
    for i, task in enumerate(tasks, 1):
        tasks_text += f"{i}. {task['text']}\n"
    
    # Отправляем пользователю новый порядок задач
    await callback.message.answer(
        tasks_text,
        reply_markup=get_tasks_inline_keyboard()
    )


async def cancel_action_inline(callback: CallbackQuery) -> None:
    """
    Отмена текущего действия
    
    Args:
        callback (CallbackQuery): Callback от кнопки отмены
    """
    # Уведомляем об отмене и возвращаем к основному меню
    await callback.message.answer("Действие отменено")
    await callback.message.answer(
        "⚡ Быстрые действия:",
        reply_markup=get_tasks_inline_keyboard()
    )
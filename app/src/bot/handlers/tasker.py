from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime
import random
from app.src.bot.states_handler.statess import TaskListForm

router = Router()

# Клавиатура для управления списком
tasks_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Завершить список"), KeyboardButton(text="🔄 Очистить список")],
        [KeyboardButton(text="📋 Показать список"), KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True
)

# Inline-клавиатура для действий с задачами
def get_tasks_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Завершить", callback_data="finish_list"),
                InlineKeyboardButton(text="🔄 Очистить", callback_data="clear_list")
            ],
            [
                InlineKeyboardButton(text="📋 Показать", callback_data="show_list"),
                InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_list")
            ],
            [
                InlineKeyboardButton(text="❌ Удалить", callback_data="delete_list")
            ]
        ]
    )

# Inline-клавиатура для редактирования
def get_edit_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Добавить задачу", callback_data="add_task"),
                InlineKeyboardButton(text="➖ Удалить задачу", callback_data="remove_task")
            ],
            [
                InlineKeyboardButton(text="📝 Переименовать", callback_data="rename_task"),
                InlineKeyboardButton(text="🔄 Перемешать", callback_data="shuffle_tasks")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
            ]
        ]
    )

# Inline-клавиатура для выбора задачи
def get_tasks_selection_keyboard(tasks, action):
    keyboard = []
    for i, task in enumerate(tasks, 1):
        keyboard.append([
            InlineKeyboardButton(text=f"{i}. {task[:30]}{'...' if len(task) > 30 else ''}", callback_data=f"{action}_{i-1}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_edit")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Inline-клавиатура для подтверждения действий
def get_confirm_inline_keyboard(action):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}"),
                InlineKeyboardButton(text="❌ Нет", callback_data="cancel_action")
            ]
        ]
    )

# Хранилище списков задач
user_task_lists = {}
# Хранилище временных данных для редактирования
user_edit_data = {}

# Начало ввода списка задач
@router.message(F.text == '/add_tasks_list')
async def start_task_list(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Инициализируем список для пользователя
    user_task_lists[user_id] = {
        'tasks': [],
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    await message.answer(
        "📝 Начинаем создание списка задач!\n\n"
        "Вводите задачи по одной. Каждое ваше сообщение будет добавлено как отдельная задача.\n\n"
        "Используйте кнопки ниже или inline-кнопки для управления списком:",
        reply_markup=tasks_keyboard
    )
    
    # Отправляем сообщение с inline-клавиатурой
    await message.answer(
        "⚡ Быстрые действия:",
        reply_markup=get_tasks_inline_keyboard()
    )
    
    await state.set_state(TaskListForm.adding_tasks)

# Обработчик inline-кнопок
@router.callback_query(F.data.in_(["finish_list", "clear_list", "show_list", "edit_list", "delete_list", "back_to_main", "add_task", "remove_task", "rename_task", "shuffle_tasks", "cancel_action", "back_to_edit"]))
async def handle_inline_buttons(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    action = callback.data
    
    await callback.answer()
    
    if action == "finish_list":
        await finish_task_list_inline(callback, state)
    elif action == "clear_list":
        await clear_task_list_inline(callback, state)
    elif action == "show_list":
        await show_current_list_inline(callback)
    elif action == "edit_list":
        await edit_list_inline(callback)
    elif action == "delete_list":
        await delete_list_inline(callback, state)
    elif action == "back_to_main":
        await back_to_main_inline(callback)
    elif action == "add_task":
        await add_task_inline(callback, state)
    elif action == "remove_task":
        await remove_task_inline(callback)
    elif action == "rename_task":
        await rename_task_inline(callback, state)
    elif action == "shuffle_tasks":
        await shuffle_tasks_inline(callback)
    elif action == "cancel_action":
        await cancel_action_inline(callback)
    elif action == "back_to_edit":
        await edit_list_inline(callback)

# Обработчик выбора задач для редактирования/удаления
@router.callback_query(F.data.startswith(("select_rename_", "select_remove_", "confirm_remove_")))
async def handle_task_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data_parts = callback.data.split('_')
    action = data_parts[0]
    
    await callback.answer()
    
    if action == "select":
        task_action = data_parts[1]  # rename или remove
        task_index = int(data_parts[2])
        
        if task_action == "rename":
            await handle_select_rename_task(callback, task_index, state)
        elif task_action == "remove":
            await handle_select_remove_task(callback, task_index)
    
    elif action == "confirm" and data_parts[1] == "remove":
        task_index = int(data_parts[2])
        await handle_confirm_remove_task(callback, task_index)

# Завершение списка через inline-кнопку
async def finish_task_list_inline(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await callback.message.answer("❌ Список пуст! Добавьте хотя бы одну задачу.")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    # Выводим финальный список в терминал
    print("=" * 70)
    print("📋 ФИНАЛЬНЫЙ СПИСОК ЗАДАЧ")
    print("=" * 70)
    print(f"👤 Пользователь: {callback.from_user.full_name} (ID: {user_id})")
    print(f"📅 Дата создания: {user_task_lists[user_id]['created_at']}")
    print(f"📊 Всего задач: {len(tasks)}")
    print("-" * 70)
    
    for i, task in enumerate(tasks, 1):
        print(f"{i:2d}. {task}")
    
    print("=" * 70)
    
    # Формируем сообщение для пользователя
    tasks_text = "✅ Ваш список задач завершен!\n\n"
    for i, task in enumerate(tasks, 1):
        tasks_text += f"{i}. {task}\n"
    
    tasks_text += f"\n📊 Всего задач: {len(tasks)}"
    
    await callback.message.answer(
        tasks_text,
        reply_markup=ReplyKeyboardMarkup(remove_keyboard=True)
    )
    
    # Очищаем состояние и список
    if user_id in user_task_lists:
        del user_task_lists[user_id]
    await state.clear()

# Очистка списка через inline-кнопку
async def clear_task_list_inline(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id in user_task_lists:
        user_task_lists[user_id]['tasks'] = []
    
    await callback.message.answer("📭 Список очищен. Начинаем заново!")
    print(f"🔄 Список очищен для пользователя {callback.from_user.full_name}")

# Показать текущий список через inline-кнопку
async def show_current_list_inline(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await callback.message.answer("📭 Список пока пуст")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    tasks_text = "📋 Текущий список задач:\n\n"
    
    for i, task in enumerate(tasks, 1):
        tasks_text += f"{i}. {task}\n"
    
    await callback.message.answer(tasks_text, reply_markup=get_tasks_inline_keyboard())

# Редактирование списка через inline-кнопку
async def edit_list_inline(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await callback.message.answer("📭 Список пуст! Нечего редактировать.")
        return
    
    await callback.message.answer(
        "✏️ Редактирование списка задач:",
        reply_markup=get_edit_inline_keyboard()
    )

# Удаление списка через inline-кнопку
async def delete_list_inline(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if user_id not in user_task_lists:
        await callback.message.answer("❌ У вас нет активных списков для удаления")
        return
    
    await callback.message.answer(
        "⚠️ Вы уверены, что хотите удалить весь список задач?",
        reply_markup=get_confirm_inline_keyboard("delete")
    )

# Обработчик подтверждения удаления всего списка
@router.callback_query(F.data == "confirm_delete")
async def handle_confirm_delete_list(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if user_id in user_task_lists:
        del user_task_lists[user_id]
    
    await callback.message.answer("🗑️ Весь список задач удален!")
    await state.clear()

# Возврат к главному меню
async def back_to_main_inline(callback: CallbackQuery):
    await callback.message.answer(
        "⚡ Быстрые действия:",
        reply_markup=get_tasks_inline_keyboard()
    )

# Добавление задачи через inline-кнопку
async def add_task_inline(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новую задачу:")
    await state.set_state(TaskListForm.adding_tasks)

# Удаление задачи через inline-кнопку
async def remove_task_inline(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await callback.message.answer("❌ Список пуст! Нечего удалять.")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    await callback.message.answer(
        "➖ Выберите задачу для удаления:",
        reply_markup=get_tasks_selection_keyboard(tasks, "select_remove")
    )

# Переименование задачи через inline-кнопку
async def rename_task_inline(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await callback.message.answer("❌ Список пуст! Нечего редактировать.")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    await callback.message.answer(
        "📝 Выберите задачу для переименования:",
        reply_markup=get_tasks_selection_keyboard(tasks, "select_rename")
    )

# Перемешивание задач через inline-кнопку
async def shuffle_tasks_inline(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await callback.message.answer("❌ Список пуст! Нечего перемешивать.")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    # Сохраняем старый порядок для логов
    old_order = tasks.copy()
    
    # Перемешиваем задачи
    random.shuffle(tasks)
    
    # Выводим в терминал
    print(f"🔄 Задачи перемешаны для пользователя {callback.from_user.full_name}")
    print("   Было:", [f"'{task}'" for task in old_order])
    print("   Стало:", [f"'{task}'" for task in tasks])
    
    # Формируем сообщение с новым порядком
    tasks_text = "🔄 Задачи перемешаны!\n\nНовый порядок:\n"
    for i, task in enumerate(tasks, 1):
        tasks_text += f"{i}. {task}\n"
    
    await callback.message.answer(
        tasks_text,
        reply_markup=get_tasks_inline_keyboard()
    )

# Обработчик выбора задачи для переименования
async def handle_select_rename_task(callback: CallbackQuery, task_index: int, state: FSMContext):
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
        'old_task': tasks[task_index]
    }
    
    await callback.message.answer(
        f"📝 Редактирование задачи №{task_index + 1}:\n"
        f"Текущий текст: {tasks[task_index]}\n\n"
        "Введите новый текст задачи:"
    )
    
    await state.set_state(TaskListForm.editing_task)

# Обработчик выбора задачи для удаления
async def handle_select_remove_task(callback: CallbackQuery, task_index: int):
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
    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_remove_{task_index}"),
                InlineKeyboardButton(text="❌ Нет", callback_data="cancel_action")
            ]
        ]
    )
    
    await callback.message.answer(
        f"⚠️ Вы уверены, что хотите удалить задачу №{task_index + 1}?\n"
        f"📝 {task_to_remove}",
        reply_markup=confirm_keyboard
    )

# Обработчик подтверждения удаления задачи
async def handle_confirm_remove_task(callback: CallbackQuery, task_index: int):
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
    print(f"➖ Удалена задача #{task_index + 1}: '{removed_task}' - {callback.from_user.full_name}")
    
    await callback.message.answer(
        f"✅ Задача №{task_index + 1} удалена!\n"
        f"📝 {removed_task}\n\n"
        f"📊 Осталось задач: {len(tasks)}",
        reply_markup=get_tasks_inline_keyboard()
    )

# Обработчик ввода нового текста задачи
@router.message(TaskListForm.editing_task)
async def process_task_edit(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id not in user_edit_data or user_edit_data[user_id]['action'] != 'renaming':
        await message.answer("❌ Ошибка редактирования")
        await state.clear()
        return
    
    if user_id not in user_task_lists:
        await message.answer("❌ Список не найден")
        await state.clear()
        return
    
    edit_data = user_edit_data[user_id]
    task_index = edit_data['task_index']
    new_text = message.text.strip()
    
    if not new_text:
        await message.answer("❌ Текст задачи не может быть пустым")
        return
    
    # Обновляем задачу
    old_text = user_task_lists[user_id]['tasks'][task_index]
    user_task_lists[user_id]['tasks'][task_index] = new_text
    
    # Выводим в терминал
    print(f"✏️ Задача #{task_index + 1} изменена:")
    print(f"   Было: '{old_text}'")
    print(f"   Стало: '{new_text}' - {message.from_user.full_name}")
    
    await message.answer(
        f"✅ Задача №{task_index + 1} успешно изменена!\n\n"
        f"📝 Было: {old_text}\n"
        f"📝 Стало: {new_text}",
        reply_markup=get_tasks_inline_keyboard()
    )
    
    # Очищаем временные данные
    if user_id in user_edit_data:
        del user_edit_data[user_id]
    
    await state.clear()

# Отмена действия
async def cancel_action_inline(callback: CallbackQuery):
    await callback.message.answer("Действие отменено")
    await callback.message.answer(
        "⚡ Быстрые действия:",
        reply_markup=get_tasks_inline_keyboard()
    )

# Обработка отмены
@router.message(F.text == "❌ Отмена")
async def cancel_task_list(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_task_lists:
        del user_task_lists[user_id]
    
    await state.clear()
    await message.answer(
        "Создание списка отменено",
        reply_markup=ReplyKeyboardMarkup(remove_keyboard=True)
    )

# Очистка списка
@router.message(F.text == "🔄 Очистить список")
async def clear_task_list(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_task_lists:
        user_task_lists[user_id]['tasks'] = []
    
    await message.answer("📭 Список очищен. Начинаем заново!")
    print(f"🔄 Список очищен для пользователя {message.from_user.full_name}")

# Показать текущий список
@router.message(F.text == "📋 Показать список")
async def show_current_list(message: Message):
    user_id = message.from_user.id
    
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await message.answer("📭 Список пока пуст")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    tasks_text = "📋 Текущий список задач:\n\n"
    
    for i, task in enumerate(tasks, 1):
        tasks_text += f"{i}. {task}\n"
    
    await message.answer(tasks_text, reply_markup=get_tasks_inline_keyboard())

# Завершение списка
@router.message(F.text == "✅ Завершить список")
async def finish_task_list(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await message.answer("❌ Список пуст! Добавьте хотя бы одну задачу.")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    # Выводим финальный список в терминал
    print("=" * 70)
    print("📋 ФИНАЛЬНЫЙ СПИСОК ЗАДАЧ")
    print("=" * 70)
    print(f"👤 Пользователь: {message.from_user.full_name} (ID: {user_id})")
    print(f"📅 Дата создания: {user_task_lists[user_id]['created_at']}")
    print(f"📊 Всего задач: {len(tasks)}")
    print("-" * 70)
    
    for i, task in enumerate(tasks, 1):
        print(f"{i:2d}. {task}")
    
    print("=" * 70)
    
    # Формируем сообщение для пользователя
    tasks_text = "✅ Ваш список задач завершен!\n\n"
    for i, task in enumerate(tasks, 1):
        tasks_text += f"{i}. {task}\n"
    
    tasks_text += f"\n📊 Всего задач: {len(tasks)}"
    
    await message.answer(
        tasks_text,
        reply_markup=ReplyKeyboardMarkup(remove_keyboard=True)
    )
    
    # Очищаем состояние и список
    if user_id in user_task_lists:
        del user_task_lists[user_id]
    await state.clear()

# Добавление задач в список
@router.message(TaskListForm.adding_tasks)
async def add_task_to_list(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Пропускаем команды кнопок
    if message.text in ["✅ Завершить список", "📋 Показать список", "🔄 Очистить список", "❌ Отмена"]:
        return
    
    # Добавляем задачу в список
    task_text = message.text.strip()
    
    if user_id in user_task_lists:
        user_task_lists[user_id]['tasks'].append(task_text)
        current_count = len(user_task_lists[user_id]['tasks'])
        
        # Выводим в терминал каждую добавленную задачу
        print(f"➕ Добавлена задача #{current_count}: '{task_text}' - {message.from_user.full_name}")
        
        await message.answer(
            f"✅ Задача #{current_count} добавлена!\n\nПродолжайте вводить задачи или используйте кнопки для управления",
            reply_markup=get_tasks_inline_keyboard()
        )

# Просмотр всех сохраненных списков
@router.message(F.text == '/my_lists')
async def show_my_lists(message: Message):
    user_id = message.from_user.id
    
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await message.answer("📭 У вас нет активных списков задач")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    # Выводим в терминал
    print("=" * 70)
    print("📋 АКТИВНЫЙ СПИСОК ЗАДАЧ ПОЛЬЗОВАТЕЛЯ")
    print("=" * 70)
    print(f"👤 Пользователь: {message.from_user.full_name}")
    print(f"📅 Создан: {user_task_lists[user_id]['created_at']}")
    print(f"📊 Задач в списке: {len(tasks)}")
    print("-" * 70)
    
    for i, task in enumerate(tasks, 1):
        print(f"{i:2d}. {task}")
    
    print("=" * 70)
    
    # Формируем сообщение для пользователя
    tasks_text = "📋 Ваш текущий список задач:\n\n"
    for i, task in enumerate(tasks, 1):
        tasks_text += f"{i}. {task}\n"
    
    tasks_text += f"\n📊 Всего задач: {len(tasks)}"
    
    await message.answer(tasks_text, reply_markup=get_tasks_inline_keyboard())

# Быстрое создание списка через разделитель
@router.message(F.text == '/quick_tasks')
async def quick_tasks_list(message: Message, state: FSMContext):
    await message.answer(
        "📝 Быстрое создание списка задач!\n\n"
        "Отправьте все задачи в одном сообщении, разделяя их переносом строки или запятыми.\n\n"
        "Пример:\n"
        "Купить продукты\n"
        "Сделать домашку\n"
        "Позвонить маме"
    )
    await state.set_state(TaskListForm.waiting_for_tasks)

# Обработка быстрого списка
@router.message(TaskListForm.waiting_for_tasks)
async def process_quick_tasks(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Разделяем задачи по разным разделителям
    text = message.text.strip()
    
    # Пробуем разные разделители
    if '\n' in text:
        tasks = [task.strip() for task in text.split('\n') if task.strip()]
    elif ',' in text:
        tasks = [task.strip() for task in text.split(',') if task.strip()]
    else:
        tasks = [text]
    
    # Фильтруем пустые задачи
    tasks = [task for task in tasks if task]
    
    if not tasks:
        await message.answer("❌ Не найдено валидных задач!")
        await state.clear()
        return
    
    # Сохраняем список
    user_task_lists[user_id] = {
        'tasks': tasks,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Выводим в терминал
    print("=" * 70)
    print("🚀 БЫСТРЫЙ СПИСОК ЗАДАЧ СОЗДАН")
    print("=" * 70)
    print(f"👤 Пользователь: {message.from_user.full_name} (ID: {user_id})")
    print(f"📅 Дата создания: {user_task_lists[user_id]['created_at']}")
    print(f"📊 Всего задач: {len(tasks)}")
    print("-" * 70)
    
    for i, task in enumerate(tasks, 1):
        print(f"{i:2d}. {task}")
    
    print("=" * 70)
    
    # Формируем сообщение для пользователя
    tasks_text = "✅ Список задач создан!\n\n"
    for i, task in enumerate(tasks, 1):
        tasks_text += f"{i}. {task}\n"
    
    tasks_text += f"\n📊 Всего задач: {len(tasks)}"
    
    await message.answer(tasks_text, reply_markup=get_tasks_inline_keyboard())
    await state.clear()
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
from .states import TaskListForm  # ✅ Импортируем состояния

router = Router()

# Клавиатура для управления списком
tasks_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Завершить список"), KeyboardButton(text="🔄 Очистить список")],
        [KeyboardButton(text="📋 Показать список"), KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True
)

# Хранилище списков задач
user_task_lists = {}

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
        "Команды:\n"
        "✅ Завершить список - закончить ввод и показать результат\n"
        "📋 Показать список - посмотреть текущий список\n"
        "🔄 Очистить список - начать заново\n"
        "❌ Отмена - отменить создание списка",
        reply_markup=tasks_keyboard
    )
    await state.set_state(TaskListForm.adding_tasks)

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
    
    await message.answer(tasks_text)

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
    
    # Очищаем состояние
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
        
        await message.answer(f"✅ Задача #{current_count} добавлена!\n\nПродолжайте вводить задачи или нажмите '✅ Завершить список'")

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
    
    await message.answer(tasks_text)

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
    
    await message.answer(tasks_text)
    await state.clear()
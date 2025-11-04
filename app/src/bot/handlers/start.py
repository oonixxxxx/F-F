from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from app.src.bot.keyboards.keyboard_handler import get_main_menu_keyboard

# Создаем роутер
start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Привет! Я бот для управления задачами.\n\n"
        "📝 Используй команды:\n"
        "• /add_tasks_list - начать создание списка задач\n"
        "• /help - получить справку\n\n"
        "Или используй кнопки ниже:",
        reply_markup=get_main_menu_keyboard()
    )

@start_router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
📋 **Доступные команды:**

• /start - начать работу с ботом
• /add_tasks_list - создать новый список задач
• /help - показать эту справку
• /cancel - отменить текущее действие

⚡ **Быстрые действия:**
После создания списка вы сможете:
• Добавлять задачи с временем и без
• Редактировать и удалять задачи
• Перемешивать порядок задач
• Сохранять и завершать списки

💡 **Советы:**
- Используйте кнопки для быстрого управления
- Задачи с временем помогают лучше планировать день
- Вы всегда можете отменить действие кнопкой 'Отмена'
"""
    await message.answer(help_text, reply_markup=get_main_menu_keyboard())

@start_router.message(Command("cancel"))
async def cmd_cancel(message: Message):
    """Обработчик команды /cancel"""
    await message.answer(
        "❌ Текущее действие отменено.",
        reply_markup=get_main_menu_keyboard()
    )

@start_router.message(F.text == "/add_tasks_list")
async def cmd_add_tasks_list(message: Message):
    """Обработчик команды добавления списка задач"""
    from app.src.bot.states_handler.statess import TaskListForm
    from app.src.bot.handlers.task_manager.task_storage import initialize_user_task_list
    from app.src.bot.keyboards.keyboard_handler import get_tasks_inline_keyboard
    
    user_id = message.from_user.id
    
    # Инициализируем список задач для пользователя
    initialize_user_task_list(
        user_id=user_id,
        username=message.from_user.username or "User",
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    await message.answer(
        "📝 Начинаем создание списка задач!\n\n"
        "Просто вводите задачи одна за другой.\n"
        "Когда закончите - нажмите '✅ Завершить список'\n\n"
        "Используйте кнопки для управления:",
        reply_markup=get_tasks_inline_keyboard()
    )
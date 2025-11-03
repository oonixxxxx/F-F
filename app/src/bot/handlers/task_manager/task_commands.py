from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.src.bot.states_handler.statess import TaskListForm
from app.src.bot.keyboards.keyboard_handler import tasks_keyboard, get_tasks_inline_keyboard
from app.src.bot.handlers.task_manager.task_service import initialize_user_task_list
from app.src.bot.handlers.task_manager.task_storage import user_task_lists

router = Router()

@router.message(F.text == '/add_tasks_list')
async def start_task_list(message: Message, state: FSMContext):
    """Начало создания списка задач"""
    user_id = message.from_user.id
    
    # Используем сервисную функцию
    initialize_user_task_list(user_id)
    
    await message.answer(
        "📝 Начинаем создание списка задач!\n\n"
        "Вводите задачи по одной. Каждое ваше сообщение будет добавлено как отдельная задача.\n\n"
        "Используйте кнопки ниже или inline-кнопки для управления списком:",
        reply_markup=tasks_keyboard
    )
    
    await message.answer(
        "⚡ Быстрые действия:",
        reply_markup=get_tasks_inline_keyboard()
    )
    
    await state.set_state(TaskListForm.adding_tasks)


@router.message(F.text == '/quick_tasks')
async def quick_tasks_list(message: Message, state: FSMContext):
    """Быстрое создание списка задач"""
    await message.answer(
        "📝 Быстрое создание списка задач!\n\n"
        "Отправьте все задачи в одном сообщении, разделяя их переносом строки или запятыми.\n\n"
        "Пример:\n"
        "Купить продукты\n"
        "Сделать домашку\n"
        "Позвонить маме"
    )
    await state.set_state(TaskListForm.waiting_for_tasks)


@router.message(F.text == '/my_lists')
async def show_my_lists(message: Message):
    """Показать мои списки"""
    user_id = message.from_user.id
    
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await message.answer("📭 У вас нет активных списков задач")
        return
    
    tasks = user_task_lists[user_id]['tasks']
    tasks_text = "📋 Ваш текущий список задач:\n\n"
    
    for i, task_data in enumerate(tasks, 1):
        task_text = task_data["text"]
        task_time = task_data.get("time")
        
        if task_time:
            tasks_text += f"{i}. {task_text} ⏱️ {task_time}\n"
        else:
            tasks_text += f"{i}. {task_text}\n"
    
    tasks_text += f"\n📊 Всего задач: {len(tasks)}"
    
    await message.answer(tasks_text, reply_markup=get_tasks_inline_keyboard())
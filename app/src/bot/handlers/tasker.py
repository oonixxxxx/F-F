from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime
import random
from handlers.states_handler.statess import TaskListForm

router = Router()

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
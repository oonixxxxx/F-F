from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.src.bot.states_handler.statess import TaskListForm
from app.src.bot.keyboards.keyboard_handler import tasks_keyboard, get_tasks_inline_keyboard
from app.src.bot.handlers.task_manager.task_service import initialize_user_task_list
from app.src.bot.handlers.task_manager.task_storage import user_task_lists

router = Router()


@router.message(F.text == '/add_tasks_list')
async def start_task_list_creation(message: Message, state: FSMContext):
    """🚀 Инициализация создания нового списка задач"""
    user_id = message.from_user.id
    
    # Инициализируем список задач для пользователя
    initialize_user_task_list(user_id)
    
    await message.answer(
        "🎯 <b>Создание списка задач</b>\n\n"
        "📝 Добавляйте задачи по одной - каждое сообщение станет новой задачей\n\n"
        "⚡ <b>Быстрые команды:</b>\n"
        "• /quick_tasks - массовое добавление\n"
        "• /my_lists - просмотр текущих списков\n"
        "• /sorted_plan - получить готовый план\n\n"
        "Используйте кнопки ниже для управления:",
        parse_mode="HTML",
        reply_markup=tasks_keyboard
    )
    
    await message.answer(
        "🔧 <b>Быстрые действия:</b>",
        parse_mode="HTML",
        reply_markup=get_tasks_inline_keyboard()
    )
    
    await state.set_state(TaskListForm.adding_tasks)


@router.message(F.text == '/quick_tasks')
async def quick_tasks_creation(message: Message, state: FSMContext):
    """⚡ Быстрое создание списка задач через массовое добавление"""
    await message.answer(
        "🚀 <b>Быстрое создание списка</b>\n\n"
        "Отправьте все задачи одним сообщением:\n\n"
        "📋 <b>Форматы:</b>\n"
        "• Через перенос строки\n"
        "• Через запятые\n"
        "• Смешанный формат\n\n"
        "🎯 <b>Примеры:</b>\n"
        "<code>Купить продукты\nСделать домашку\nПозвонить маме</code>\n\n"
        "Или:\n"
        "<code>Задача 1, Задача 2, Задача 3</code>",
        parse_mode="HTML"
    )
    await state.set_state(TaskListForm.waiting_for_tasks)


@router.message(F.text == '/my_lists')
async def display_user_tasks(message: Message):
    """📊 Отображение текущих списков задач пользователя"""
    user_id = message.from_user.id
    
    # Проверяем наличие активных списков
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await message.answer(
            "📭 <b>Списки задач пусты</b>\n\n"
            "Используйте /add_tasks_list чтобы начать создание",
            parse_mode="HTML"
        )
        return
    
    tasks = user_task_lists[user_id]['tasks']
    
    # Формируем красивый вывод задач
    tasks_text = "📋 <b>Ваш список задач</b>\n\n"
    
    for i, task_data in enumerate(tasks, 1):
        task_text = task_data["text"]
        task_time = task_data.get("time")
        
        task_display = f"{i}. {task_text}"
        if task_time:
            task_display += f" ⏰ {task_time}"
        
        tasks_text += task_display + "\n"
    
    # Добавляем статистику
    tasks_text += f"\n📊 <b>Статистика:</b> {len(tasks)} задач"
    
    await message.answer(
        tasks_text, 
        parse_mode="HTML",
        reply_markup=get_tasks_inline_keyboard()
    )


@router.message(F.text == "/sorted_plan")
async def generate_sorted_plan(message: Message):
    """🎯 Генерация отсортированного плана задач"""
    user_id = message.from_user.id
    
    # Проверяем наличие задач
    if user_id not in user_task_lists or not user_task_lists[user_id]['tasks']:
        await message.answer(
            "❌ <b>Нет задач для сортировки</b>\n\n"
            "Сначала создайте список задач через /add_tasks_list",
            parse_mode="HTML"
        )
        return
    
    # Получаем отсортированные задачи
    sorted_tasks = await ask_qwen_to_sort_tasks(user_id)
    
    if sorted_tasks:
        # Форматируем красивый вывод
        plan_text = "🎯 <b>Ваш оптимальный план:</b>\n\n"
        
        for i, task in enumerate(sorted_tasks, 1):
            task_title = task.get('title', 'Без названия')
            task_priority = task.get('priority', '')
            task_time = task.get('time', '')
            
            task_line = f"{i}. {task_title}"
            if task_priority:
                task_line += f" {get_priority_emoji(task_priority)}"
            if task_time:
                task_line += f" ⏰ {task_time}"
            
            plan_text += task_line + "\n"
        
        plan_text += f"\n✅ Готово! Всего задач: {len(sorted_tasks)}"
    else:
        plan_text = "⚠️ <b>Не удалось создать план</b>\n\nПопробуйте позже или обратитесь в поддержку"
    
    await message.answer(plan_text, parse_mode="HTML")


async def ask_qwen_to_sort_tasks(user_id: int):
    """
    🎯 Функция сортировки задач
    TODO: Реализовать интеграцию с Qwen
    """
    if user_id in user_task_lists and user_task_lists[user_id]['tasks']:
        tasks = user_task_lists[user_id]['tasks']
        return [{"title": task["text"], "priority": "medium"} for task in tasks]
    return None


def get_priority_emoji(priority: str) -> str:
    """🔤 Получение эмодзи для приоритета"""
    priority_emojis = {
        "high": "🔴",
        "medium": "🟡", 
        "low": "🟢"
    }
    return priority_emojis.get(priority, "⚪")
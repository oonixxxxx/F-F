from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from datetime import datetime

from app.src.bot.states_handler.statess import TaskListForm
from app.src.bot.keyboards.keyboard_handler import get_tasks_inline_keyboard, get_time_suggestion_keyboard
from app.src.bot.handlers.task_manager.task_service import add_simple_task, create_task_data, save_task_with_time
from app.src.bot.handlers.task_manager.task_storage import user_task_lists, user_edit_data

router = Router()


@router.message(TaskListForm.adding_tasks)
async def add_task_to_list(message: Message, state: FSMContext):
    """Обработчик добавления задач в состоянии adding_tasks"""
    user_id = message.from_user.id
    
    # Игнорирование команд кнопок
    button_commands = [
        "✅ Завершить список", "📋 Показать список", 
        "🔄 Очистить список", "❌ Отмена"
    ]
    if message.text in button_commands:
        return
    
    # Добавляем задачу через сервис
    await add_simple_task(message, user_id)


@router.message(TaskListForm.waiting_for_tasks)
async def process_quick_tasks(message: Message, state: FSMContext):
    """Обработка быстрого создания списка"""
    user_id = message.from_user.id
    
    # Разделяем задачи по разным разделителям
    text = message.text.strip()
    
    if '\n' in text:
        tasks_texts = [task.strip() for task in text.split('\n') if task.strip()]
    elif ',' in text:
        tasks_texts = [task.strip() for task in text.split(',') if task.strip()]
    else:
        tasks_texts = [text]
    
    # Фильтруем пустые задачи
    tasks_texts = [task for task in tasks_texts if task]
    
    if not tasks_texts:
        await message.answer("❌ Не найдено валидных задач!")
        await state.clear()
        return
    
    # Создаем задачи БЕЗ времени
    tasks_data = [create_task_data(task_text) for task_text in tasks_texts]
    
    # Сохраняем список
    user_task_lists[user_id] = {
        'tasks': tasks_data,
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Логирование
    print(f"🚀 Быстрый список создан: {len(tasks_data)} задач - {message.from_user.full_name}")
    
    # Формируем сообщение для пользователя
    tasks_text = "✅ Список задач создан!\n\n"
    for i, task_data in enumerate(tasks_data, 1):
        tasks_text += f"{i}. {task_data['text']}\n"
    
    tasks_text += f"\n📊 Всего задач: {len(tasks_data)}"
    
    await message.answer(tasks_text, reply_markup=get_tasks_inline_keyboard())
    await state.clear()


@router.message(TaskListForm.waiting_for_task_text)
async def process_task_text_input(message: Message, state: FSMContext):
    """Обработка введенного текста задачи для добавления с временем"""
    user_id = message.from_user.id
    
    if user_id not in user_edit_data:
        await message.answer("❌ Ошибка процесса. Начните заново.")
        await state.clear()
        return
    
    task_text = message.text.strip()
    
    # Валидация текста задачи
    if not task_text:
        await message.answer("❌ Текст задачи не может быть пустым. Введите текст задачи:")
        return
    
    if len(task_text) > 200:
        await message.answer("❌ Текст задачи слишком длинный (макс. 200 символов). Введите короче:")
        return
    
    # Сохраняем текст задачи во временные данные
    user_edit_data[user_id]['task_text'] = task_text
    user_edit_data[user_id]['step'] = 'waiting_for_time'
    
    # Просим ввести время с подсказками
    await message.answer(
        f"⏱️ Теперь введите время для задачи:\n"
        f"📝 '{task_text}'\n\n"
        f"Можно ввести своё время или выбрать из предложенных:",
        reply_markup=get_time_suggestion_keyboard()
    )
    
    # Переходим в состояние ожидания времени
    await state.set_state(TaskListForm.waiting_for_task_time)


@router.message(TaskListForm.waiting_for_task_time)
async def process_custom_time_input(message: Message, state: FSMContext):
    """Обработка ручного ввода времени"""
    user_id = message.from_user.id
    
    if user_id not in user_edit_data:
        await message.answer("❌ Ошибка процесса. Начните заново.")
        await state.clear()
        return
    
    time_input = message.text.strip()
    
    # Базовая валидация времени
    if not time_input:
        await message.answer("❌ Время не может быть пустым. Введите время:")
        return
    
    if len(time_input) > 50:
        await message.answer("❌ Слишком длинное описание времени. Введите короче:")
        return
    
    await save_task_with_time(message, state, time_input)


@router.message(TaskListForm.editing_task)
async def process_task_edit(message: Message, state: FSMContext):
    """Обработчик редактирования задачи"""
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
    old_text = user_task_lists[user_id]['tasks'][task_index]['text']
    user_task_lists[user_id]['tasks'][task_index]['text'] = new_text
    
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
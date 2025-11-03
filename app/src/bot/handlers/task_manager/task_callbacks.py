# Импорты необходимых модулей и классов
from aiogram import Router, F  # Router для создания маршрутизатора, F для фильтров
from aiogram.types import CallbackQuery  # Тип данных для обработки callback-запросов от inline-кнопок
from aiogram.fsm.context import FSMContext  # Контекст машины состояний для управления состояниями бота

# Импорт состояний бота
from app.src.bot.states_handler.statess import TaskListForm

# Импорт функций для создания клавиатур
from app.src.bot.keyboards.keyboard_handler import (
    get_tasks_inline_keyboard,  # Клавиатура для управления задачами
    get_tasks_selection_keyboard,  # Клавиатура для выбора задач
    get_confirm_inline_keyboard  # Клавиатура для подтверждения действий
)

# Импорт сервисных функций для работы с задачами
from app.src.bot.handlers.task_manager.task_service import (
    finish_task_list,  # Завершение списка задач
    clear_task_list,  # Очистка списка задач
    show_current_list,  # Показать текущий список
    edit_list,  # Редактирование списка
    delete_list,  # Удаление списка
    add_task_with_time_handler,  # Добавление задачи с временем
    handle_time_suggestion,  # Обработка предложений времени
    time_custom_handler,  # Обработка пользовательского времени
    cancel_time_input_handler,  # Отмена ввода времени
    back_to_main_inline,  # Возврат к главному меню
    add_task_inline,  # Добавление задачи через inline
    remove_task_inline,  # Удаление задачи через inline
    rename_task_inline,  # Переименование задачи через inline
    shuffle_tasks_inline,  # Перемешивание задач через inline
    cancel_action_inline  # Отмена действия через inline
)

# Импорт хранилищ данных пользователей
from .task_storage import user_task_lists, user_edit_data  # Глобальные словари для хранения данных пользователей

# Создание роутера для обработки callback-запросов
router = Router()


# Основной обработчик inline-кнопок - централизованная точка входа
@router.callback_query(F.data.in_([
    "finish_list", "clear_list", "show_list", "edit_list", 
    "delete_list", "back_to_main", "add_task", "remove_task", 
    "rename_task", "shuffle_tasks", "cancel_action", "back_to_edit",
    "add_task_with_time", "time_custom", "cancel_time_input"
]))
async def handle_inline_buttons(callback: CallbackQuery, state: FSMContext):
    """
    Единая точка входа для обработки inline-кнопок
    
    Args:
        callback (CallbackQuery): Объект callback-запроса от кнопки
        state (FSMContext): Контекст машины состояний для управления состояниями бота
    """
    
    # Получаем ID пользователя для идентификации его данных
    user_id = callback.from_user.id
    # Получаем действие из данных callback
    action = callback.data
    
    # Подтверждаем получение callback (убирает "часики" на кнопке)
    await callback.answer()
    
    # Словарь-маршрутизатор: связывает действия с соответствующими функциями-обработчиками
    action_handlers = {
        # Действия управления списками задач
        "finish_list": finish_task_list,  # Завершить список задач
        "clear_list": clear_task_list,  # Очистить список задач
        "show_list": show_current_list,  # Показать текущий список
        "edit_list": edit_list,  # Перейти в режим редактирования
        "delete_list": delete_list,  # Запрос на удаление списка
        
        # Навигационные действия
        "back_to_main": back_to_main_inline,  # Вернуться в главное меню
        "back_to_edit": edit_list,  # Вернуться к редактированию
        
        # Действия с отдельными задачами
        "add_task": add_task_inline,  # Добавить задачу
        "remove_task": remove_task_inline,  # Удалить задачу
        "rename_task": rename_task_inline,  # Переименовать задачу
        "shuffle_tasks": shuffle_tasks_inline,  # Перемешать задачи
        
        # Действия отмены
        "cancel_action": cancel_action_inline,  # Отменить текущее действие
        "cancel_time_input": cancel_time_input_handler,  # Отменить ввод времени
        
        # Действия связанные с временем
        "add_task_with_time": add_task_with_time_handler,  # Добавить задачу с временем
        "time_custom": time_custom_handler,  # Ввод пользовательского времени
    }
    
    # Получаем соответствующий обработчик для действия
    handler = action_handlers.get(action)
    
    if handler:
        # Если обработчик найден - выполняем его
        await handler(callback, state)
    else:
        # Обработка callback-ов времени (15min, 30min, etc)
        # Проверяем, начинается ли действие с "time_"
        if action.startswith("time_"):
            await handle_time_suggestion(callback, state)


# Обработчик выбора задач для редактирования/удаления
@router.callback_query(F.data.startswith(("select_rename_", "select_remove_", "confirm_remove_")))
async def handle_task_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора задач для редактирования/удаления
    
    Args:
        callback (CallbackQuery): Callback от inline-кнопки выбора задачи
        state (FSMContext): Контекст машины состояний
    """
    
    user_id = callback.from_user.id
    # Разбиваем данные callback на части для анализа
    # Например: "select_rename_0" -> ["select", "rename", "0"]
    data_parts = callback.data.split('_')
    action_type = data_parts[0]  # "select" или "confirm"
    
    # Подтверждаем получение callback
    await callback.answer()
    
    # Обработка выбора задачи (для переименования или удаления)
    if action_type == "select":
        task_action = data_parts[1]  # "rename" или "remove"
        task_index = int(data_parts[2])  # Индекс задачи (преобразуем в число)
        
        if task_action == "rename":
            # Обработка выбора задачи для переименования
            await handle_select_rename_task(callback, task_index, state)
        elif task_action == "remove":
            # Обработка выбора задачи для удаления
            await handle_select_remove_task(callback, task_index)
    
    # Обработка подтверждения удаления задачи
    elif action_type == "confirm" and data_parts[1] == "remove":
        task_index = int(data_parts[2])  # Индекс задачи для удаления
        await handle_confirm_remove_task(callback, task_index)


# Обработчик подтверждения удаления всего списка задач
@router.callback_query(F.data == "confirm_delete")
async def handle_confirm_delete_list(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подтверждения удаления всего списка задач
    
    Args:
        callback (CallbackQuery): Callback от кнопки подтверждения
        state (FSMContext): Контекст машины состояний
    """
    
    user_id = callback.from_user.id
    
    # Удаляем весь список задач пользователя из хранилища
    if user_id in user_task_lists:
        del user_task_lists[user_id]
    
    # Уведомляем пользователя об успешном удалении
    await callback.message.answer("🗑️ Весь список задач удален!")
    # Очищаем состояние машины состояний
    await state.clear()


# Вспомогательная функция: обработка выбора задачи для переименования
async def handle_select_rename_task(callback: CallbackQuery, task_index: int, state: FSMContext):
    """
    Обработчик выбора задачи для переименования
    
    Args:
        callback (CallbackQuery): Callback от кнопки выбора
        task_index (int): Индекс выбранной задачи в списке
        state (FSMContext): Контекст машины состояний
    """
    
    user_id = callback.from_user.id
    
    # Проверяем существование списка задач пользователя
    if user_id not in user_task_lists:
        await callback.message.answer("❌ Список не найден")
        return
    
    # Получаем список задач пользователя
    tasks = user_task_lists[user_id]['tasks']
    
    # Проверяем валидность индекса задачи
    if task_index < 0 or task_index >= len(tasks):
        await callback.message.answer("❌ Неверный номер задачи")
        return
    
    # Сохраняем данные для редактирования в глобальном хранилище
    user_edit_data[user_id] = {
        'action': 'renaming',  # Тип действия - переименование
        'task_index': task_index,  # Индекс редактируемой задачи
        'old_task': tasks[task_index]['text']  # Старый текст задачи для reference
    }
    
    # Запрашиваем у пользователя новый текст задачи
    await callback.message.answer(
        f"📝 Редактирование задачи №{task_index + 1}:\n"
        f"Текущий текст: {tasks[task_index]['text']}\n\n"
        "Введите новый текст задачи:"
    )
    
    # Устанавливаем состояние "редактирование задачи"
    await state.set_state(TaskListForm.editing_task)


# Вспомогательная функция: обработка выбора задачи для удаления
async def handle_select_remove_task(callback: CallbackQuery, task_index: int):
    """
    Обработчик выбора задачи для удаления
    
    Args:
        callback (CallbackQuery): Callback от кнопки выбора
        task_index (int): Индекс выбранной задачи в списке
    """
    
    user_id = callback.from_user.id
    
    # Проверяем существование списка задач пользователя
    if user_id not in user_task_lists:
        await callback.message.answer("❌ Список не найден")
        return
    
    # Получаем список задач пользователя
    tasks = user_task_lists[user_id]['tasks']
    
    # Проверяем валидность индекса задачи
    if task_index < 0 or task_index >= len(tasks):
        await callback.message.answer("❌ Неверный номер задачи")
        return
    
    # Получаем задачу для удаления
    task_to_remove = tasks[task_index]
    
    # Создаем клавиатуру подтверждения для конкретной задачи
    # Генерируем уникальный идентификатор для callback_data
    confirm_keyboard = get_confirm_inline_keyboard(f"remove_{task_index}")
    
    # Запрашиваем подтверждение удаления у пользователя
    await callback.message.answer(
        f"⚠️ Вы уверены, что хотите удалить задачу №{task_index + 1}?\n"
        f"📝 {task_to_remove['text']}",
        reply_markup=confirm_keyboard  # Добавляем клавиатуру с кнопками подтверждения
    )


# Вспомогательная функция: обработка подтверждения удаления задачи
async def handle_confirm_remove_task(callback: CallbackQuery, task_index: int):
    """
    Обработчик подтверждения удаления задачи
    
    Args:
        callback (CallbackQuery): Callback от кнопки подтверждения
        task_index (int): Индекс удаляемой задачи в списке
    """
    
    user_id = callback.from_user.id
    
    # Проверяем существование списка задач пользователя
    if user_id not in user_task_lists:
        await callback.message.answer("❌ Список не найден")
        return
    
    # Получаем список задач пользователя
    tasks = user_task_lists[user_id]['tasks']
    
    # Проверяем валидность индекса задачи
    if task_index < 0 or task_index >= len(tasks):
        await callback.message.answer("❌ Неверный номер задачи")
        return
    
    # Удаляем задачу из списка и сохраняем ее данные для отображения
    removed_task = tasks.pop(task_index)
    
    # Логируем действие удаления в терминал для отладки
    print(f"➖ Удалена задача #{task_index + 1}: '{removed_task['text']}' - {callback.from_user.full_name}")
    
    # Уведомляем пользователя об успешном удалении
    await callback.message.answer(
        f"✅ Задача №{task_index + 1} удалена!\n"
        f"📝 {removed_task['text']}\n\n"
        f"📊 Осталось задач: {len(tasks)}",
        reply_markup=get_tasks_inline_keyboard()  # Обновляем клавиатуру управления
    )
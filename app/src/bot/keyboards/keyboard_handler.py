from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, 
    KeyboardButton
)

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📅 Создать план на сегодня", callback_data="create_today_plan")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="show_stats"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="show_settings")
    )
    builder.row(
        InlineKeyboardButton(text="📢 Наш канал", url="https://t.me/your_channel")
    )
    
    return builder.as_markup()

def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu"))
    return builder.as_markup()

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
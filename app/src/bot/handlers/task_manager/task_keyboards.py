from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Этот файл содержит дополнительные клавиатуры, специфичные для задач
# Основные клавиатуры остаются в keyboard_handler.py

def get_task_operations_keyboard():
    """Клавиатура для операций с конкретной задачей"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Переименовать", callback_data="rename_task"),
                InlineKeyboardButton(text="⏱️ Изменить время", callback_data="edit_task_time")
            ],
            [
                InlineKeyboardButton(text="✅ Выполнить", callback_data="complete_task"),
                InlineKeyboardButton(text="➖ Удалить", callback_data="remove_task")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад к списку", callback_data="back_to_list")
            ]
        ]
    )


def get_task_time_edit_keyboard():
    """Клавиатура для редактирования времени задачи"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏱️ 15 мин", callback_data="edit_time_15min"),
                InlineKeyboardButton(text="⏱️ 30 мин", callback_data="edit_time_30min")
            ],
            [
                InlineKeyboardButton(text="⏱️ 1 час", callback_data="edit_time_1h"),
                InlineKeyboardButton(text="⏱️ 2 часа", callback_data="edit_time_2h")
            ],
            [
                InlineKeyboardButton(text="❌ Убрать время", callback_data="remove_time"),
                InlineKeyboardButton(text="✏️ Своё время", callback_data="custom_time")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_task")
            ]
        ]
    )
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

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
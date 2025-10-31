from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.src.bot.keyboards.keyboard_handler import get_back_to_menu_keyboard, get_main_menu_keyboard

router = Router()

# Обработчик для создания плана
@router.callback_query(F.data == "create_today_plan")
async def create_today_plan(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Создаем план на сегодня...")
    
    # Здесь может быть логика создания плана
    await callback.message.edit_text(
        "📝 Давайте создадим план на сегодня!\n\n"
        "Что вы хотите сделать?",
        reply_markup=get_back_to_menu_keyboard()
    )

# Обработчик для статистики
@router.callback_query(F.data == "show_stats")
async def show_stats(callback: CallbackQuery):
    await callback.answer("Загружаем статистику...")
    
    # Здесь может быть логика получения статистики
    await callback.message.edit_text(
        "📊 Ваша статистика:\n\n"
        "• Выполнено задач: 15\n"
        "• В процессе: 3\n"
        "• Производительность: 85%",
        reply_markup=get_back_to_menu_keyboard()
    )

# Обработчик для возврата в меню
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # Очищаем состояние если использовали FSM
    await callback.message.edit_text(
        "🏠 Главное меню",
        reply_markup=get_main_menu_keyboard()
    )
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

router = Router()

# Callback с параметром (например: task_complete_123)
@router.callback_query(F.data.startswith("task_complete_"))
async def complete_task(callback: CallbackQuery):
    task_id = callback.data.split("_")[-1]  # Извлекаем ID задачи
    
    await callback.answer(f"Задача {task_id} выполнена!", show_alert=True)
    
    # Обновляем сообщение или делаем другие действия
    await callback.message.edit_text(
        f"✅ Задача {task_id} отмечена выполненной!",
        reply_markup=callback.message.reply_markup  # Сохраняем клавиатуру
    )

# Callback для выбора времени
@router.callback_query(F.data.startswith("time_"))
async def select_time(callback: CallbackQuery, state: FSMContext):
    selected_time = callback.data.split("_")[1]
    
    # Сохраняем в состоянии
    await state.update_data(selected_time=selected_time)
    
    await callback.answer(f"Выбрано время: {selected_time}")
    await callback.message.edit_text(f"🕐 Вы выбрали время: {selected_time}")
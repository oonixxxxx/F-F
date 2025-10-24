from aiogram import Dispatcher
from aiogram import types
from aiogram import Router
from aiogram import F
from aiogram.types import Message

# Создаем роутер
router = Router()

@router.message(F.text == 'hui')
async def hui(message: Message):
    await message.answer('hui hui hui')

# Функция для регистрации всех обработчиков
def register_all_handlers(dp: Dispatcher):
    dp.include_router(router)
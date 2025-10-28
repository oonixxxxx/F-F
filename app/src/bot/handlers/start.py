from aiogram import Router, types
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import datetime 

from app.src.bot.keyboadrs.keyboard_handler import get_main_menu_keyboard
from app.src.bot.handlers.functions import print_user_info, save_user_to_json

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    '''
    Функция которая заносит пользователя 
    в json файл
    '''
    
    user_id = message.from_user.id #id пользователя 
    username = message.from_user.username # никнейм пользователя 
    first_name = message.from_user.first_name # имя пользователя

    if message.from_user.last_name: #при наличии фамилии у пользователя в тг
        last_name = message.from_user.last_name 
    
    # Выводим информацию о пользователе в терминал
    print_user_info(user_id, username, first_name, last_name)
    
    # Сохраняем в базу данных
    save_user_to_json(user_id, username, first_name, last_name)
    
    await message.answer(
        f"Привет, {first_name}! Я бот который поможет тебе расспределить твое время правильно", 
        reply_markup=get_main_menu_keyboard()
    )
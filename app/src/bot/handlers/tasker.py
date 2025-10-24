from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == '/add_firstname')
async def add_task_handler(message: Message):
    await message.answer('Send your firstname')

@router.message(F.text == '/add_secondname')
async def add_task_handler(message: Message):
    first_name = message.from_user.first_name
    await message.answer(f'Send your secondname? {first_name}')
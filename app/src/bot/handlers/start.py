from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == '/start')
async def start_handler(message: Message):
    await message.answer('Hello! Welcome to the bot! Send "add_task" to add a task.')
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram import Router
from aiogram import F
from aiogram.types import Message

router = Router()

@router.message(F.text == 'hui')
async def hui(message: Message):
    await message.answer('hui hui hui')
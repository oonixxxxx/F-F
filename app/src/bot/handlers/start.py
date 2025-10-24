from aiogram import types
from aiogram.dispatcher import Dispatcher

async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

def register_start_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.src.bot.handlers import router

import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.src.bot.handlers import router

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

API_TOKEN = '7817640220:AAHwWlUDh-bez2BQA3pNflc1BMnvcWo3Cyw'

async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=API_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Подключаем роутеры
    dp.include_router(router)
    
    print("🤖 Бот запущен...")
    print("💾 Данные сохраняются в JSON файл")
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
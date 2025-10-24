import asyncio
import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import register_all_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)

router = Router()

API_TOKEN = '7817640220:AAHwWlUDh-bez2BQA3pNflc1BMnvcWo3Cyw'

async def main():
    # Создаем бот и диспетчер с хранилищем
    bot = Bot(token=API_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем роутер
    dp.include_router(router)
    
    # Регистрируем все обработчики
    register_all_handlers(dp)
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
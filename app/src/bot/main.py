import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.src.bot.handlers import router

# Configure logging
logging.basicConfig(level=logging.INFO)

API_TOKEN = ''

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Import and register handlers
    dp.include_router(router)
    
    # Delete webhook and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
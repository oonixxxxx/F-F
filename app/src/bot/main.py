import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers.states_handler.statess import TaskListForm

# Configure logging
logging.basicConfig(level=logging.INFO)

API_TOKEN = '7817640220:AAHwWlUDh-bez2BQA3pNflc1BMnvcWo3Cyw'

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Import and register handlers
    from handlers import router
    dp.include_router(router)
    
    # Delete webhook and start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
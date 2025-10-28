import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers.states_handler.statess import TaskListForm

# Импортируем из одного места
from app.src.bot.handlers import start_router, main_menu_router, today_plan_router
from app.src.bot.api_token import API_TOKEN

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(start_router)
    dp.include_router(main_menu_router) 
    dp.include_router(today_plan_router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
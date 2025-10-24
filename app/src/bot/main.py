import logging
from aiogram import Bot, Dispatcher, executor
from app.src.bot.config_bot import SimpleConfig
from handlers import register_all_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)

API_TOKEN = SimpleConfig.get_secret_value()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Регистрируем все обработчики
register_all_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
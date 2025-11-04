from aiogram import Router

from app.src.bot.handlers.start import start_router
from app.src.bot.handlers.task_manager import router as task_manager_router

# Создаем главный роутер
router = Router()

# Включаем под-роутеры
router.include_router(start_router)
router.include_router(task_manager_router)

__all__ = ['router']
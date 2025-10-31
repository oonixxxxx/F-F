from aiogram import Router
from . import start
from app.src.bot.handlers.task_manager import task_router  # Импортируем новый роутер

router = Router()

# Include all routers
router.include_router(start.router)
router.include_router(task_router)  # Заменяем старый tasker.router на новый task_router

__all__ = ['router']
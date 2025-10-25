from aiogram import Router
from . import start, tasker

router = Router()

# Include all routers
router.include_router(start.router)
router.include_router(tasker.router)
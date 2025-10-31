from .task_commands import router as commands_router
from .task_states import router as states_router  
from .task_callbacks import router as callbacks_router

# Объединяем все роутеры
task_router = commands_router
task_router.include_router(states_router)
task_router.include_router(callbacks_router)

__all__ = ['task_router']
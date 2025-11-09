import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, insert, update
#from app.src.database.models import User, Task, AISortedTask  # твои модели
from models import User, Task, AISortedTask


#import secret as ss
#from app.src.database import secret as ss
#import app.src.database.API as api

import secret as ss
import API as api

# Асинхронный движок
engine = create_async_engine(ss.DATABASE_URL)

# Асинхронная фабрика сессий
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)



async def init_db():
    # Опционально: создать таблицы, если их ещё нет
    async with engine.begin() as conn:
        # Если БД уже есть, можно не вызывать:
        # await conn.run_sync(Base.metadata.create_all)

        print("✅ Подключение к БД успешно (SQLAlchemy).")


# Пример: получить настройки пользователя
async def get_user_prefs(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            return {"productivity_time": user.productivity_time, "notes": user.notes}
        return None


# Пример: получить задачи пользователя
async def get_user_tasks(user_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Task).where(Task.user_id == user_id))
        tasks = result.scalars().all()
        return [{"title": t.title, "priority": t.priority} for t in tasks]


# Пример: сохранить настройки
async def save_user_prefs(user_id: int, prod_time: str, notes: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        if user:
            # Обновляем
            await session.execute(
                update(User)
                .where(User.user_id == user_id)
                .values(productivity_time=prod_time, notes=notes)
            )
        else:
            # Вставляем
            new_user = User(user_id=user_id, productivity_time=prod_time, notes=notes)
            session.add(new_user)
        await session.commit()


# Пример: сохранить задачу
async def save_user_tasks(user_id: int, title: str, priority: int):
    async with AsyncSessionLocal() as session:
        new_task = Task(user_id=user_id, title=title, priority=priority)
        session.add(new_task)
        await session.commit()


# Тест
async def test_db():
    await init_db()
    await save_user_prefs(12345, "вечер", "с утра плохо")
    
    result = await api.ask_qwen_to_sort_tasks(12345) 
    print(result)



if __name__ == "__main__":
    asyncio.run(test_db())

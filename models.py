from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func


from sqlalchemy.ext.asyncio import async_sessionmaker

Base = declarative_base()


# Таблица пользователей
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    productivity_time = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Таблица задач
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    title = Column(String, nullable=False)
    priority = Column(Integer, default=1)
    done = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Таблица отсортированных задач от ИИ
class AISortedTask(Base):
    __tablename__ = 'ai_sorted_tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    sorted_tasks = Column(Text, nullable=False)  # или JSON если хочешь
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    task_date = Column(DateTime(timezone=True))  # опционально
    source_tasks_hash = Column(String)  # опционально
    model_used = Column(String, default='Qwen3')  # опционально

import asyncio
import asyncpg 
import logging
from contextlib import asynccontextmanager

import secret as ss
import DB_logging as lgn 


pool = None  # набор открытых соединений с БД 
logger = logging.getLogger(__name__)


async def init_db():
    global pool  
    real_pool = await asyncpg.create_pool(ss.DATABASE_URL)
    pool = lgn.LoggingPool(real_pool)


@asynccontextmanager
async def get_db_connection():
    '''
    суть функции в том, чтобы стать контекстным менеджером и избежать копипасты

    работает она следующим образом:
    1. происходит соединение с бд при помощи pool.acquire() 
    2. затем это соединение передается в блок yeild conn
    3. и ты можешь использовать conn для выполнения запросов 
    4. после выхода из контекстного менеджера вызываются методы и 
        соединение возвращается в pool, а не закрывается
    '''
    async with pool.acquire() as conn:
        wrapped_conn = lgn.LoggingConnection(conn)
        yield wrapped_conn  



async def get_user_prefs(user_id: int):
    async with get_db_connection() as conn:
        # $1 - позволяет избежать sql инъенкций 
        query = "SELECT productivity_time, notes FROM users WHERE user_id = $1"
        row = await conn.fetchrow(query, user_id)  # выполняет запрос и возвращает 
        return row 


async def save_user_prefs(user_id: int, prod_time: str, notes: str):
    async with get_db_connection() as conn:
        query = """
                INSERT INTO users (user_id, productivity_time, notes)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE SET 
                    productivity_time = EXCLUDED.productivity_time,
                    notes = EXCLUDED.notes;
        """
        await conn.execute(query, user_id, prod_time, notes)


async def get_user_tasks(user_id: int):
    async with get_db_connection() as conn:
        query = "SELECT title, priority FROM tasks WHERE user_id=$1"
        row = await conn.fetchrow(query, user_id)
        return row 


async def save_user_tasks(user_id: int, title: str, priority: int):
    async with get_db_connection() as conn:
        query = """
            INSERT INTO tasks (user_id, title, priority, created_at)
            VALUES ($1, $2, $3, $4)
        """
        await conn.execute(query, user_id, title, priority, created_at)


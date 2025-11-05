import asyncpg
import logging
from contextlib import asynccontextmanager
import asyncio 

import secret as ss
import DB_logging as lgn 


pool = None  # наборы соединений с бд 
logger = logging.getLogger(__name__)


async def init_db():
    global pool  
    real_pool = await asyncpg.create_pool(ss.DATABASE_URL)
    pool = real_pool


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
            INSERT INTO tasks (user_id, title, priority)
            VALUES ($1, $2, $3)
        """
        await conn.execute(query, user_id, title, priority)#, created_at)


async def del_user_task(user_id: int, title: str):
    async with get_db_connection() as conn:
        query = """
            
        """


async def test_db_connection():
    """
    Тестирует подключение к БД: пингует, создаёт тестовую таблицу (если нужно),
    вставляет и читает данные.
    """
    try:
        async with get_db_connection() as conn:
            # Проверим, можем ли мы выполнить простой запрос
            await conn.execute("SELECT 1;")
            print("✅ Подключение к БД успешно установлено.")

            # Попробуем вставить тестовую запись в таблицу users
            await conn.execute(
                "INSERT INTO users (user_id, productivity_time, notes) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO NOTHING;",
                99998, "тест", "проверка подключения из Python"
            )
            print("✅ Тестовая запись добавлена (или проигнорирована, если уже существует).")

            # Попробуем получить запись
            row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", 99998)
            if row:
                print(f"✅ Данные из БД: {dict(row)}")
            else:
                print("⚠️ Запись не найдена (неожиданно).")

    except Exception as e:
        print(f"❌ Ошибка при подключении к БД: {e}")
        return False

    print("✅ Подключение к БД работает корректно!")
    return True


async def main():
    await init_db()
    await test_db_connection()


if __name__ == "__main__":
    asyncio.run(main())

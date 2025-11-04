import asyncpg
import logging 


logger = logging.getLogger(__name__)


class LoggingConnection:
    def __init__(self, conn):
        self._conn = conn

    async def execute(self, query, *args, *kwargs):
        # оставляю args и kwargs, потому что можно будет потом
        # делать с этими аргументами 
        logger.info(f"Executing SQL: {query} | Args: {args}")
        try:
            result = await self._conn.execute(query, *args, **kwargs)
            logger.info("Execute successful.")
            return result
        except Exception as e:
            logger.error(f"Execute failed: {e}")
            raise 

    async def fetchrow(self, query, *args, **kwargs):
        logger.info(f"Fetching row: {query} | Args: {args}")
        try:
            result = await self._conn.fetchrow(query, *args, **kwargs)
            logger.info(f"Fetched row: {result}")
            return result
        except Exception as e:
            logger.error(f"Fetchrow failed: {e}")
            raise 

    async def fetch(self, query, *args, **kwargs):
        logger.info(f"Fetching rows: {query} | Args: {args}")
        try:
            result = await self._conn.fetch(query, *args, **kwargs)
            logger.info(f"Fetched {len(result)} rows.")
            return result 
        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            raise

    def __getattr__(self, name):
        return getattr(self._conn, name)



class LoggingPool:
    def __init__(self, pool):
        self._pool = pool 

    async def acquire(self):
        conn = await self._pool.acquire()
        return LoggingConnection(conn)

    async def release(self, conn):
        await self._pool.release(conn._conn)

    async def close(self):
        await self._pool.close()

    def __getattr__(self, name):
        return getattr(self._pool, name)

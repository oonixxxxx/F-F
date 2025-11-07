import asyncpg
import logging

logger = logging.getLogger(__name__)

class LoggingConnection:
    def __init__(self, conn):
        self._conn = conn

    async def execute(self, query, *args, **kwargs):
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
        '''
        чтобы не логировать, абсолютно все методы из asyncpg,
        я перенаправляю с помощью getattr(self._conn, name) в библиотеку
        asyncpg и там они уже как то обрабатываются
        '''
        return getattr(self._conn, name)


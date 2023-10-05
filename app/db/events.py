import os
from fastapi import FastAPI
from databases import Database
from app.core.config import DATABASE_URL, MIN_CONNECTION_COUNT, MAX_CONNECTION_COUNT
from app.core.logging import get_logger


db_events_logger = get_logger(__name__)


async def establish_connection_pool(app: FastAPI) -> None:
    DB_URL = f"{DATABASE_URL}_test" if os.environ.get("TESTING") else DATABASE_URL
    database = Database(
        DB_URL, 
        min_size=MIN_CONNECTION_COUNT, 
        max_size=MAX_CONNECTION_COUNT
    )

    try:
        await database.connect()
        app.state._conn_pool = database
    except Exception as exc:
        db_events_logger.exception(exc)


async def release_connection_pool(app: FastAPI) -> None:
    try:
        await app.state._conn_pool.disconnect()
    except Exception as exc:
        db_events_logger.exception(exc)

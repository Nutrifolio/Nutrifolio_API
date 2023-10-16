import os
import redis.asyncio as redis
from fastapi import FastAPI
from app.core.config import REDIS_URL
from app.core.logging import get_logger


cache_events_logger = get_logger(__name__)


async def establish_cache_connection_pool(app: FastAPI) -> None:
    CACHE_URL = f"{REDIS_URL}_test" if os.environ.get("TESTING") else REDIS_URL

    try:
        cache = await redis.from_url(
            CACHE_URL, encoding="utf-8", decode_responses=True
        )
        app.state._cache_conn_pool = cache
    except Exception as exc:
        cache_events_logger.exception(exc)


async def release_cache_connection_pool(app: FastAPI) -> None:
    try:
        await app.state._cache_conn_pool.aclose()
    except Exception as exc:
        cache_events_logger.exception(exc)

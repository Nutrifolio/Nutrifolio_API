from typing import Callable
from fastapi import FastAPI
from app.db.events import establish_connection_pool, release_connection_pool


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        await establish_connection_pool(app)
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        await release_connection_pool(app)
    return stop_app

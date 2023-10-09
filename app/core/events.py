import boto3
from typing import Callable
from fastapi import FastAPI
from app.core.config import DO_ACCESS_KEY, DO_SECRET_KEY, DO_SPACE_BUCKET_URL
from app.db.events import establish_connection_pool, release_connection_pool


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        await establish_connection_pool(app)
        app.state._sb_client = boto3.client(
            's3',
            region_name='fra1',
            endpoint_url=DO_SPACE_BUCKET_URL,
            aws_access_key_id=DO_ACCESS_KEY,
            aws_secret_access_key=str(DO_SECRET_KEY)
        )
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        await release_connection_pool(app)
        app.state._sb_client.close()
    return stop_app

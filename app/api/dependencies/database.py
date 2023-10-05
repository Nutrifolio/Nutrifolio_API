from typing import Callable, Type, Annotated
from fastapi import Depends
from fastapi.requests import Request
from databases import Database
from app.db.repositories.base import BaseRepository


def get_database(request: Request) -> Database:
    return request.app.state._conn_pool


def get_repository(repo_type: Type[BaseRepository]) -> Callable:
    def get_repo(db: Annotated[Database, Depends(get_database)]) -> Type[BaseRepository]:
        return repo_type(db)
    return get_repo

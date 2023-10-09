from pydantic import EmailStr
from fastapi import HTTPException, status
from app.db.repositories.base import BaseRepository
from app.models.stores import StoreCreate, StoreInDB
from app.services import auth_service
from databases import Database


GET_STORE_BY_ID_QUERY = """
    SELECT id, email, password, is_verified
    FROM stores
    WHERE id = :id;
"""

GET_STORE_BY_EMAIL_QUERY = """
    SELECT id, email, password, is_verified
    FROM stores
    WHERE email = :email;
"""
 
REGISTER_NEW_STORE_QUERY = """
    INSERT INTO stores (email, password)
    VALUES (:email, :password)
    RETURNING id, email, password, is_verified;
"""


class StoresRepository(BaseRepository):
    """"
    All database actions associated with the Store resource
    """

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.auth_service = auth_service
    

    async def get_store_by_id(self, *, store_id: int) -> StoreInDB:
        store_record = await self.db.fetch_one(
            query=GET_STORE_BY_ID_QUERY,
            values={"id": store_id}
        )

        if not store_record:
            return None

        return StoreInDB(**store_record)


    async def get_store_by_email(self, *, email: EmailStr) -> StoreInDB:
        store_record = await self.db.fetch_one(
            query=GET_STORE_BY_EMAIL_QUERY,
            values={"email": email}
        )

        if not store_record:
            return None

        return StoreInDB(**store_record)


    async def register_new_store(self, *, new_store: StoreCreate) -> StoreInDB:
        hashed_password = self.auth_service.hash_password(
            password=new_store.password
        )

        new_store = new_store.model_copy(
            update={'password': hashed_password}
        )

        created_store_record = await self.db.fetch_one(
            query=REGISTER_NEW_STORE_QUERY, 
            values={**new_store.model_dump(exclude={'conf_password'})}
        )

        return StoreInDB(**created_store_record)

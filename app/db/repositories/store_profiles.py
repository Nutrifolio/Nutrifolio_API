from typing import Optional
from pydantic import EmailStr
from fastapi import HTTPException, status
from app.db.repositories.base import BaseRepository
from app.models.store_profiles import StoreProfileInDB, StoreProfileCreate
from app.services import auth_service
from databases import Database


GET_STORE_PROFILE_BY_STORE_ID_QUERY = """
    SELECT id, name, logo_url, phone_number, address, lat, lng, store_id
    FROM store_profiles
    WHERE store_id = :store_id;
"""

GET_STORE_PROFILE_BY_NAME_QUERY = """
    SELECT id, name, logo_url, phone_number, address, lat, lng, store_id
    FROM store_profiles
    WHERE name = :name;
"""

CREATE_NEW_STORE_PROFILE_QUERY = """
    INSERT INTO store_profiles (name, logo_url, phone_number, address, lat, lng, location, store_id)
    VALUES (:name, :logo_url, :phone_number, :address, :lat, :lng, ST_MakePoint(:lng, :lat)::geography, :store_id)
    RETURNING id, name, logo_url, phone_number, address, lat, lng, store_id;
"""


class StoreProfilesRepository(BaseRepository):
    """"
    All database actions associated with the StoreProfile resource
    """


    async def get_store_profile_by_id(self, *, store_id: int) -> StoreProfileInDB:
        store_profile_record = await self.db.fetch_one(
            query=GET_STORE_PROFILE_BY_STORE_ID_QUERY,
            values={"store_id": store_id}
        )

        if not store_profile_record:
            return None

        return StoreProfileInDB(**store_profile_record)


    async def get_store_profile_by_name(self, *, name: str) -> StoreProfileInDB:
        store_profile_record = await self.db.fetch_one(
            query=GET_STORE_PROFILE_BY_NAME_QUERY,
            values={"name": name}
        )

        if not store_profile_record:
            return None

        return StoreProfileInDB(**store_profile_record)


    async def create_new_store_profile(
        self, *, new_store_profile: StoreProfileCreate
    ) -> StoreProfileInDB:
        created_store_profile_record = await self.db.fetch_one(
            query=CREATE_NEW_STORE_PROFILE_QUERY, 
            values={**new_store_profile.model_dump()}
        )

        return StoreProfileInDB(**created_store_profile_record)

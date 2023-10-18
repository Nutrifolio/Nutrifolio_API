from typing import Optional
from pydantic import EmailStr
from fastapi import HTTPException, status
from app.db.repositories.base import BaseRepository
from app.models.store_profiles import StoreProfileInDB, StoreProfileCreate, StoreProfileOutFilter
from app.api.enums.products import MaxDistanceOption
from app.services import auth_service
from databases import Database


GET_NEARBY_STORE_IDS_QUERY = """
    SELECT store_id
    FROM store_profiles
    WHERE ST_DWithin(
        location,
        ST_MakePoint(:lng, :lat)::geography,
        :max_dist * 1000
    );
"""

GET_STORE_PROFILE_FILTER_VIEW_BY_STORE_ID_QUERY = """
    SELECT
        store_id AS id, name, logo_url,
        ST_Distance(
            location,
            ST_MakePoint(:lng, :lat)::geography
        )/1000 AS distance_km
    FROM store_profiles
    WHERE store_id = :store_id;
"""

GET_STORE_PROFILE_SIMPLE_VIEW_BY_STORE_ID_QUERY = """
    SELECT
        id, name, description, logo_url, phone_number, address, 
        lat, lng, store_id
    FROM store_profiles
    WHERE store_id = :store_id;
"""

GET_STORE_PROFILE_BY_STORE_ID_QUERY = """
    SELECT 
        id, name, description, logo_url, phone_number, address, 
        lat, lng, store_id
    FROM store_profiles
    WHERE store_id = :store_id;
"""

GET_STORE_PROFILE_BY_NAME_QUERY = """
    SELECT 
        id, name, description, logo_url, phone_number, address, 
        lat, lng, store_id
    FROM store_profiles
    WHERE name = :name;
"""

CREATE_NEW_STORE_PROFILE_QUERY = """
    INSERT INTO store_profiles (
        name, description, logo_url, phone_number, address, 
        lat, lng, location, store_id
    )
    VALUES (
        :name, :description, :logo_url, :phone_number, :address, 
        :lat, :lng, ST_MakePoint(:lng, :lat)::geography, :store_id
    )
    RETURNING
        id, name, description, logo_url, phone_number, address, 
        lat, lng, store_id;
"""


class StoreProfilesRepository(BaseRepository):
    """"
    All database actions associated with the StoreProfile resource
    """

    async def get_nearby_store_ids(
        self,
        *,
        cache: "Redis",
        lat: float,
        lng: float,
        max_dist: MaxDistanceOption,
        EMPTY_LIST_INDICATOR: int = -1
    ) -> list[int]:
        key = hash((lat, lng, max_dist))
        if await cache.exists(key):
            store_ids = await cache.lrange(key, 0, -1)
            if EMPTY_LIST_INDICATOR in store_ids:
                return []
            return [int(store_id) for store_id in store_ids]

        store_profile_records = await self.db.fetch_all(
            query=GET_NEARBY_STORE_IDS_QUERY,
            values={"lat": lat, "lng": lng, "max_dist": max_dist}
        )
        store_ids = [
            record["store_id"] for record in store_profile_records
        ]
        if len(store_ids) > 0:
            await cache.rpush(key, *store_ids)
            await cache.expire(key, 300)
        else:
            await cache.rpush(key, EMPTY_LIST_INDICATOR)
            await cache.expire(key, 300)
        return [int(store_id) for store_id in store_ids]


    async def get_store_profile_filter_view_by_store_id(
        self,
        *,
        store_id: int,
        lat: float,
        lng: float
    ) -> StoreProfileOutFilter:
        store_profile_record = await self.db.fetch_one(
            query=GET_STORE_PROFILE_FILTER_VIEW_BY_STORE_ID_QUERY,
            values={"store_id": store_id, "lat": lat, "lng": lng}
        )

        if not store_profile_record:
            return None

        return StoreProfileOutFilter(**store_profile_record)


    async def get_store_profile_simple_view_by_store_id(
        self, *, store_id: int
    ) -> StoreProfileInDB:
        store_profile_record = await self.db.fetch_one(
            query=GET_STORE_PROFILE_SIMPLE_VIEW_BY_STORE_ID_QUERY,
            values={"store_id": store_id}
        )

        if not store_profile_record:
            return None

        return StoreProfileInDB(**store_profile_record)


    async def get_store_profile_by_store_id(self, *, store_id: int) -> StoreProfileInDB:
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

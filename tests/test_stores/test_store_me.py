import pytest
import pytest_asyncio
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.stores import StoreInDB
from app.models.store_profiles import StoreProfileCreate, StoreProfileInDB, StoreProfileOut
from app.db.repositories.store_profiles import StoreProfilesRepository


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestStoreMe:
    @pytest_asyncio.fixture
    async def verified_test_store_profile(
        self,
        verified_test_store: StoreInDB, 
        store_profile_repo: StoreProfilesRepository
    ) -> StoreInDB:
        new_store_profile = StoreProfileCreate(
            name="test_store",
            description="test_desc",
            phone_number=6943444546,
            address="test_address",
            lat=38.214,
            lng=23.812,
            store_id=verified_test_store.id
        )

        return await store_profile_repo.create_new_store_profile(
            new_store_profile=new_store_profile
        )

    async def test_authenticated_store_can_retrieve_own_data(
        self,
        app: FastAPI,
        authorized_client_for_verified_test_store: AsyncClient,
        verified_test_store_profile: StoreProfileInDB,
    ) -> None:
        res = await authorized_client_for_verified_test_store.get(
            app.url_path_for("get-current-store-profile-info")
        )
        assert res.status_code == status.HTTP_200_OK

        store_profile = StoreProfileOut(**res.json())
        assert store_profile.id == verified_test_store_profile.id
        assert store_profile.name == verified_test_store_profile.name
        assert store_profile.logo_url == verified_test_store_profile.logo_url
        assert store_profile.phone_number == verified_test_store_profile.phone_number
        assert store_profile.address == verified_test_store_profile.address
        assert store_profile.lat == verified_test_store_profile.lat
        assert store_profile.lng == verified_test_store_profile.lng
        assert store_profile.store_id == verified_test_store_profile.store_id


    async def test_store_cannot_access_own_data_if_not_authenticated(
        self, app: FastAPI, client: AsyncClient, test_store: StoreProfileInDB,
    ) -> None:
        res = await client.get(app.url_path_for("get-current-store-profile-info"))
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

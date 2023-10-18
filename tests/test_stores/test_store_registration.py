import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.stores import StoreInDB
from app.models.store_profiles import StoreProfileCreate, StoreProfileInDB, StoreProfileOut
from app.db.repositories.stores import StoresRepository
from app.db.repositories.store_profiles import StoreProfilesRepository
from app.services import auth_service


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestStoreRegistration:
    async def test_stores_can_register_successfully_without_logo(
        self,
        app: FastAPI,
        client: AsyncClient,
        store_repo: StoresRepository,
        store_profile_repo: StoreProfilesRepository,
    ) -> None:
        data = {
            "email": "test_email@mystore.com",
            "password": "mysecretpassword",
            "conf_password": "mysecretpassword",
            "name": "test_store",
            "description": "test_desc",
            "phone_number": 6943444546,
            "address": "test_address",
            "lat": 38.214,
            "lng": 23.812
        }

        db_store = await store_repo.get_store_by_email(email=data["email"])
        assert db_store is None

        res = await client.post(
            app.url_path_for("register-new-store"),
            data=data
        )
        assert res.status_code == status.HTTP_201_CREATED

        db_store = await store_repo.get_store_by_email(email=data["email"])
        assert db_store is not None
        assert db_store.email == data["email"]
        assert db_store.password != data["password"] # should be hashed
        assert auth_service.verify_password(
            password=data["password"],
            hashed_password=db_store.password,
        )

        db_store_profile = await store_profile_repo.get_store_profile_by_name(
            name=data["name"]
        )
        assert db_store_profile is not None
        assert db_store_profile.name == data["name"]
        assert db_store_profile.logo_url is None
        assert db_store_profile.phone_number == data["phone_number"]
        assert db_store_profile.address == data["address"]
        assert db_store_profile.lat == data["lat"]
        assert db_store_profile.lng == data["lng"]

        detail = res.json().get("detail")
        assert detail == "Successfully submitted for review."


    async def test_stores_can_register_successfully_with_logo(
        self,
        app: FastAPI,
        client: AsyncClient,
        store_repo: StoresRepository,
        store_profile_repo: StoreProfilesRepository,
        mock_sb_client
    ) -> None:
        data = {
            "email": "test_email@mystore.com",
            "password": "mysecretpassword",
            "conf_password": "mysecretpassword",
            "name": "test_store",
            "description": "test_desc",
            "phone_number": 6943444546,
            "address": "test_address",
            "lat": 38.214,
            "lng": 23.812
        }
        files = {"logo_image": open("./tests/assets/Nutrifolio-logo.png", "rb")}

        db_store = await store_repo.get_store_by_email(email=data["email"])
        assert db_store is None
        db_store_profile = await store_profile_repo.get_store_profile_by_name(name=data["name"])
        assert db_store_profile is None

        res = await client.post(
            app.url_path_for("register-new-store"),
            data=data,
            files=files
        )
        assert res.status_code == status.HTTP_201_CREATED

        db_store = await store_repo.get_store_by_email(email=data["email"])
        assert db_store is not None
        assert db_store.email == data["email"]
        assert db_store.password != data["password"] # should be hashed
        assert auth_service.verify_password(
            password=data["password"],
            hashed_password=db_store.password,
        )

        db_store_profile = await store_profile_repo.get_store_profile_by_name(name=data["name"])
        assert db_store_profile is not None
        assert db_store_profile.name == data["name"]
        assert data["name"] in db_store_profile.logo_url
        assert db_store_profile.phone_number == data["phone_number"]
        assert db_store_profile.address == data["address"]
        assert db_store_profile.lat == data["lat"]
        assert db_store_profile.lng == data["lng"]

        detail = res.json().get("detail")
        assert detail == "Successfully submitted for review."


    async def test_store_registration_fails_when_email_is_taken(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_store: StoreInDB,
        test_store_profile: StoreProfileInDB,
        store_repo: StoresRepository,
        store_profile_repo: StoreProfilesRepository,
    ) -> None:
        data = {
            "email": "test_email@mystore.com",
            "password": "mysecretpassword",
            "conf_password": "mysecretpassword",
            "name": "non_taken_name",
            "description": "test_desc",
            "phone_number": 6943444546,
            "address": "test_address",
            "lat": 38.214,
            "lng": 23.812
        }

        db_store = await store_repo.get_store_by_email(email=data["email"])
        assert db_store is not None
        db_store_profile = await store_profile_repo.get_store_profile_by_name(name=data["name"])
        assert db_store_profile is None

        res = await client.post(
            app.url_path_for("register-new-store"),
            data=data
        )
        assert res.status_code == status.HTTP_409_CONFLICT
        assert data["email"] in res.json().get("detail")
        assert data["name"] not in res.json().get("detail")


    async def test_store_registration_fails_when_store_name_is_taken(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_store: StoreInDB,
        test_store_profile: StoreProfileInDB,
        store_repo: StoresRepository,
        store_profile_repo: StoreProfilesRepository,
    ) -> None:
        data = {
            "email": "non_taken_email@mystore.com",
            "password": "mysecretpassword",
            "conf_password": "mysecretpassword",
            "name": "test_store",
            "description": "test_desc",
            "phone_number": 6943444546,
            "address": "test_address",
            "lat": 38.214,
            "lng": 23.812
        }

        db_store = await store_repo.get_store_by_email(email=data["email"])
        assert db_store is None
        db_store_profile = await store_profile_repo.get_store_profile_by_name(name=data["name"])
        assert db_store_profile is not None

        res = await client.post(
            app.url_path_for("register-new-store"),
            data=data
        )
        assert res.status_code == status.HTTP_409_CONFLICT
        assert data["name"] in res.json().get("detail")
        assert data["email"] not in res.json().get("detail")


    @pytest.mark.parametrize(
        "payload, status_code",
        (
            ({
                "email": "not_taken_email@mystore.com", 
                "password": "short",
                "conf_password": "short",
                "name": "non_taken_name",
                "description": "test_desc",
                "phone_number": 6943444546,
                "address": "test_address",
                "lat": 38.214,
                "lng": 23.812
            }, 422), # weak password
            ({
                "email": "not_taken_email@mystore.com", 
                "password": "mysecretpassword_1",
                "conf_password": "mysecretpassword_2",
                "name": "non_taken_name",
                "description": "test_desc",
                "phone_number": 6943444546,
                "address": "test_address",
                "lat": 38.214,
                "lng": 23.812
            }, 422), # not matching passwords
        )
    )
    async def test_store_registration_fails_with_invalid_payload(
        self, app: FastAPI, client: AsyncClient,
        payload: dict, status_code: int,
    ) -> None:
        res = await client.post(
            app.url_path_for("register-new-store"),
            data=payload
        )
        assert res.status_code == status_code

import jwt
import pytest
from fastapi import FastAPI, status, HTTPException
from httpx import AsyncClient
from app.models.stores import StoreCreate, StoreInDB
from app.models.store_profiles import StoreProfileInDB, StoreProfileOut
from app.db.repositories.stores import StoresRepository
from app.db.repositories.store_profiles import StoreProfilesRepository
from app.core.config import SECRET_KEY, JWT_ALGORITHM
from app.services import auth_service
from databases import Database


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestStoreRegistration:
    @pytest.fixture
    def store_repo(self, db: Database) -> StoresRepository:
        return StoresRepository(db)


    @pytest.fixture
    def store_profile_repo(self, db: Database) -> StoreProfilesRepository:
        return StoreProfilesRepository(db)


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


class TestStoreLogin:
    async def test_verified_store_can_login_successfully_and_receives_valid_token(
        self, app: FastAPI, client: AsyncClient, verified_test_store: StoreInDB,
    ) -> None:
        login_data = {
            "username": verified_test_store.email,
            "password": "mysecretpassword",  # test store's plaintext password
        }

        res = await client.post(
            app.url_path_for("store-login"),
            headers={"content-type": "application/x-www-form-urlencoded"},
            data=login_data
        )
        assert res.status_code == status.HTTP_200_OK

        token_type = res.json().get("token_type")
        assert token_type == "bearer"

        access_token = res.json().get("access_token")
        payload = jwt.decode(
            access_token, str(SECRET_KEY), algorithms=[JWT_ALGORITHM]
        )
        assert payload["store_id"] == verified_test_store.id


    async def test_non_verified_store_cannot_login_successfully(
        self, app: FastAPI, client: AsyncClient, test_store: StoreInDB,
    ) -> None:
        login_data = {
            "username": test_store.email,
            "password": "mysecretpassword",  # test store's plaintext password
        }

        res = await client.post(
            app.url_path_for("store-login"),
            headers={"content-type": "application/x-www-form-urlencoded"},
            data=login_data
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

        detail = res.json().get("detail")
        assert detail == "Store verification is pending, we will contact you via an email when the process has finished."


    @pytest.mark.parametrize(
        "credential, wrong_value, status_code",
        (
            ("email", "wrong@email.com", 401),
            ("email", "not_email", 401),
            ("email", None, 422),
            ("password", "wrongpassword", 401),
            ("password", None, 422),
        ),
    )
    async def test_store_with_wrong_creds_doesnt_receive_token(
        self, app: FastAPI, client: AsyncClient, test_store: StoreInDB,
        credential: str, wrong_value: str, status_code: int,
    ) -> None:
        store_data = test_store.model_dump()
        store_data["password"] = "mysecretpassword" # test store's plaintext password
        store_data[credential] = wrong_value

        login_data = {
            "username": store_data["email"],
            "password": store_data["password"],
        }
 
        res = await client.post(
            app.url_path_for("store-login"),
            headers={"content-type": "application/x-www-form-urlencoded"},
            data=login_data
        )
        assert res.status_code == status_code
        assert "access_token" not in res.json()


class TestStoreMe:
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

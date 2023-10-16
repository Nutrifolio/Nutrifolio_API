import jwt
import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.stores import StoreInDB
from app.core.config import SECRET_KEY, JWT_ALGORITHM


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


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

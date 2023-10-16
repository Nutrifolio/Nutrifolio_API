import jwt
import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.users import UserInDB
from app.core.config import SECRET_KEY, JWT_ALGORITHM


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestUserLogin:
    async def test_user_can_login_successfully_and_receives_valid_token(
        self, app: FastAPI, client: AsyncClient, test_user: UserInDB,
    ) -> None:
        login_data = {
            "username": test_user.email,
            "password": "mysecretpassword",  # test user's plaintext password
        }

        res = await client.post(
            app.url_path_for("user-login"),
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
        assert payload["user_id"] == test_user.id

 
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
    async def test_user_with_wrong_creds_doesnt_receive_token(
        self, app: FastAPI, client: AsyncClient, test_user: UserInDB,
        credential: str, wrong_value: str, status_code: int,
    ) -> None:
        user_data = test_user.model_dump()
        user_data["password"] = "mysecretpassword" # test user's plaintext pwd
        user_data[credential] = wrong_value

        login_data = {
            "username": user_data["email"],
            "password": user_data["password"],
        }
 
        res = await client.post(
            app.url_path_for("user-login"),
            headers={"content-type": "application/x-www-form-urlencoded"},
            data=login_data
        )
        assert res.status_code == status_code
        assert "access_token" not in res.json()

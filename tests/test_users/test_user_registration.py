import jwt
import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.users import UserInDB
from app.db.repositories.users import UsersRepository
from app.core.config import SECRET_KEY, JWT_ALGORITHM
from app.services import auth_service


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestUserRegistration:
    async def test_users_can_register_successfully(
        self, app: FastAPI, client: AsyncClient, user_repo: UsersRepository,
    ) -> None:
        new_user = {
            "email": "test_email@gmail.com",
            "password": "mysecretpassword",
            "conf_password": "mysecretpassword"
        }

        db_user = await user_repo.get_user_by_email(email=new_user["email"])
        assert db_user is None

        res = await client.post(
            app.url_path_for("register-new-user"), 
            json={"new_user": new_user}
        )
        assert res.status_code == status.HTTP_201_CREATED

        db_user = await user_repo.get_user_by_email(email=new_user["email"])
        assert db_user is not None
        assert db_user.email == new_user["email"]
        assert db_user.password != new_user["password"] # should be hashed
        assert auth_service.verify_password(
            password=new_user["password"],
            hashed_password=db_user.password,
        )

        token_type = res.json().get("token_type")
        assert token_type == "bearer"

        access_token = res.json().get("access_token")
        payload = jwt.decode(
            access_token, str(SECRET_KEY), algorithms=[JWT_ALGORITHM]
        )
        assert payload["user_id"] == db_user.id


    async def test_user_registration_fails_when_email_is_taken(
        self, app: FastAPI, client: AsyncClient, test_user: UserInDB,
    ) -> None:
        new_user = {
            "email": "test_email@gmail.com", 
            "password": "mysecretpassword",
            "conf_password": "mysecretpassword"
        }
        assert test_user.email == new_user["email"]

        res = await client.post(
            app.url_path_for("register-new-user"),
            json={"new_user": new_user}
        )
        assert res.status_code == status.HTTP_409_CONFLICT


    @pytest.mark.parametrize(
        "payload, status_code",
        (
            ({
                "email": "not_taken_email@gmail.com", 
                "password": "short",
                "conf_password": "short"
            }, 422), # weak password
            ({
                "email": "not_taken_email@gmail.com", 
                "password": "mysecretpassword_1",
                "conf_password": "mysecretpassword_2"
            }, 422), # not matching passwords
        )
    )
    async def test_user_registration_fails_with_invalid_payload(
        self, app: FastAPI, client: AsyncClient,
        payload: dict, status_code: int,
    ) -> None:
        res = await client.post(
            app.url_path_for("register-new-user"),
            json={"new_user": payload}
        )
        assert res.status_code == status_code

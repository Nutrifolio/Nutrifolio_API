import jwt
import pytest
from fastapi import FastAPI, status, HTTPException
from httpx import AsyncClient
from app.models.users import UserCreate, UserInDB, UserOut
from app.db.repositories.users import UsersRepository
from app.core.config import SECRET_KEY, JWT_ALGORITHM
from app.services import auth_service
from databases import Database


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestUserRegistration:
    async def test_users_can_register_successfully(
        self, app: FastAPI, client: AsyncClient, db: Database,
    ) -> None:
        user_repo = UsersRepository(db)
        new_user = {
            "username": "test_username",
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
        assert db_user.username == new_user["username"]
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
            "username": "test_username",
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
                "password": "mysecretpassword",
                "conf_password": "mysecretpassword"
            }, 422), # missing username
            ({
                "username": "not_taken_username",
                "email": "not_taken_email@gmail.com", 
                "password": "short",
                "conf_password": "short"
            }, 422), # weak password
            ({
                "username": "not_taken_username",
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


class TestUserLogin:
    async def test_user_can_login_successfully_and_receives_valid_token(
        self, app: FastAPI, client: AsyncClient, test_user: UserInDB,
    ) -> None:
        login_data = {
            "username": test_user.email,
            "password": "mysecretpassword",  # insert user's plaintext password
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
        user_data["password"] = "mysecretpassword"
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


class TestUserMe:
    async def test_authenticated_user_can_retrieve_own_data(
        self,
        app: FastAPI,
        authorized_client_for_test_user: AsyncClient,
        test_user: UserInDB,
    ) -> None:
        res = await authorized_client_for_test_user.get(
            app.url_path_for("get-current-user-info")
        )
        assert res.status_code == status.HTTP_200_OK

        user = UserOut(**res.json())
        assert user.id == test_user.id
 

    async def test_user_cannot_access_own_data_if_not_authenticated(
        self, app: FastAPI, client: AsyncClient, test_user: UserInDB,
    ) -> None:
        res = await client.get(app.url_path_for("get-current-user-info"))
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

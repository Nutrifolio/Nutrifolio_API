import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.users import UserInDB, UserOut


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


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

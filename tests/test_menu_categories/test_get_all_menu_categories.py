import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestGetAllMenuCategories:
    async def test_get_all_menu_categories(
        self,
        app: FastAPI,
        client: AsyncClient
    ) -> None:
        res = await client.get(app.url_path_for("get-all-menu-categories"))
        assert res.status_code == status.HTTP_200_OK

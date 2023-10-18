import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestGetAllTags:
    async def test_get_all_tags(
        self,
        app: FastAPI,
        client: AsyncClient
    ) -> None:
        res = await client.get(app.url_path_for("get-all-tags"))
        assert res.status_code == status.HTTP_200_OK

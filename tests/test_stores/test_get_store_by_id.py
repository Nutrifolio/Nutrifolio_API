import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.products import ProductInDB
from app.models.store_profiles import StoreProfileInDB
from app.models.product_tags import ProductTagInDB
from app.models.product_menu_categories import ProductMenuCategoryInDB
from fixtures.test_stores_fixtures import (
    verified_test_store,
    verified_test_store_profile,
    test_products
)


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestGetStoreById:
    async def test_get_store_by_id(
        self,
        app: FastAPI,
        client: AsyncClient,
        verified_test_store_profile: StoreProfileInDB,
        test_products: list[ProductInDB]
    ) -> None:
        res = await client.get(
            app.url_path_for(
                "get-store-by-id",
                id=verified_test_store_profile.store_id
            )
        )
        assert res.status_code == status.HTTP_200_OK

        assert verified_test_store_profile.id == res.json().get("id")
        assert verified_test_store_profile.name == res.json().get("name")
        assert verified_test_store_profile.logo_url == res.json().get("logo_url")
        assert verified_test_store_profile.lat == res.json().get("lat")
        assert verified_test_store_profile.lng == res.json().get("lng")

        products_by_menu_categories = res.json().get("products_by_menu_categories")

        product_1 = products_by_menu_categories[0]["products"][0]
        assert product_1["name"] == "test_product_1"

        product_2 = products_by_menu_categories[0]["products"][1]
        assert product_2["name"] == "test_product_2"

        product_1 = products_by_menu_categories[1]["products"][0]
        assert product_1["name"] == "test_product_1"


    async def test_get_product_by_id_that_does_not_exist_fails(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_products: list[ProductInDB]
    ) -> None:
        res = await client.get(
            app.url_path_for("get-store-by-id", id=500)
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND


    async def test_get_store_by_invalid_id(
        self,
        app: FastAPI,
        client: AsyncClient,
        verified_test_store_profile: StoreProfileInDB
    ) -> None:
        res = await client.get(
            app.url_path_for("get-store-by-id", id=-1)
        )
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.products import ProductInDB
from app.models.product_details import ProductDetailsInDB
from app.models.store_profiles import StoreProfileInDB
from app.models.product_tags import ProductTagInDB
from app.models.product_menu_categories import ProductMenuCategoryInDB
from fixtures.test_get_product_by_id_fixtures import (
    test_product,
    test_product_details,
    test_product_tags,
    test_product_menu_categories
)


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestGetProductById:
    async def test_get_product_by_id(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_product: ProductInDB,
        test_product_details: ProductDetailsInDB,
        test_store_profile: StoreProfileInDB,
        test_product_tags: list[ProductTagInDB],
        test_product_menu_categories: list[ProductMenuCategoryInDB]
    ) -> None:
        res = await client.get(
            app.url_path_for("get-product-by-id", id=test_product.id)
        )
        assert res.status_code == status.HTTP_200_OK

        product = res.json().get("product")
        assert test_product.id == product["id"]
        assert test_product.name == product["name"]
        assert test_product.description == product["description"]
        assert test_product.image_url == product["image_url"]
        assert test_product.price == product["price"]

        details = product["details"]
        assert details["calories"] == test_product_details.calories
        assert details["protein"] == test_product_details.protein
        assert details["carbs"] == test_product_details.carbs
        assert details["fiber"] == test_product_details.fiber
        assert details["sugars"] == test_product_details.sugars
        assert details["fat"] == test_product_details.fat
        assert details["saturated_fat"] == test_product_details.saturated_fat

        tags = product["tags"]
        assert len(tags) == len(test_product_tags)
        for tag in test_product_tags:
            assert tag.tag_id in [t["id"] for t in tags]

        menu_categories = product["menu_categories"]
        assert len(menu_categories) == len(test_product_menu_categories)
        for menu_category in test_product_menu_categories:
            assert menu_category.menu_category_id in [
                mc["id"] for mc in menu_categories
            ]


    async def test_get_product_by_id_that_does_not_exist_fails(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_product: ProductInDB,
        test_product_details: ProductDetailsInDB,
        test_product_tags: list[ProductTagInDB],
        test_product_menu_categories: list[ProductMenuCategoryInDB]
    ) -> None:
        res = await client.get(
            app.url_path_for("get-product-by-id", id=500)
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND


    async def test_get_product_by_invalid_id(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_product: ProductInDB,
        test_product_details: ProductDetailsInDB,
        test_product_tags: list[ProductTagInDB],
        test_product_menu_categories: list[ProductMenuCategoryInDB]
    ) -> None:
        res = await client.get(
            app.url_path_for("get-product-by-id", id=-1)
        )
        assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

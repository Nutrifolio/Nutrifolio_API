import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.products import ProductInDB
from fixtures.test_filter_products_from_nearby_stores_fixtures import (
    test_store_1, test_store_2,
    test_store_1_profile, test_store_2_profile,
    test_products_test_store_1, test_products_test_store_2
)


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestFilterProductsFromNearbyStores:
    async def test_filter_without_stores_nearby(
        self,
        app: FastAPI,
        client: AsyncClient,
        cache: "Redis",
        test_products_test_store_1: list[ProductInDB],
        test_products_test_store_2: list[ProductInDB]
    ) -> None:
        params = {
            "lat": 38,
            "lng": 23,
            "max_dist": 5,
            "min_price": 0.0,
            "max_price": 10.0,
            "sort_by": "price",
            "sort_order": "ASC",
            "tag_ids": [1],
            "menu_category_ids": [1]
        }
        res = await client.get(
            app.url_path_for("filter-products-from-nearby-stores"),
            params=params
        )
        assert res.status_code == status.HTTP_200_OK

        products_by_menu_categories = \
            res.json().get("products_by_menu_categories")
        assert len(products_by_menu_categories) == 0


    async def test_filter_single_menu_category_order_price_asc(
        self,
        app: FastAPI,
        client: AsyncClient,
        cache: "Redis",
        test_products_test_store_1: list[ProductInDB],
        test_products_test_store_2: list[ProductInDB]
    ) -> None:
        params = {
            "lat": 38,
            "lng": 23.8,
            "max_dist": 5,
            "min_price": 0.0,
            "max_price": 5.0,
            "sort_by": "price",
            "sort_order": "ASC",
            "tag_ids": [1],
            "menu_category_ids": [1]
        }
        res = await client.get(
            app.url_path_for("filter-products-from-nearby-stores"),
            params=params
        )
        assert res.status_code == status.HTTP_200_OK

        products_by_menu_categories = \
            res.json().get("products_by_menu_categories")
        
        a, c = products_by_menu_categories[0]["products"]
        assert a["name"] == "test_product_a"
        assert c["name"] == "test_product_c"


    async def test_filter_single_menu_category_order_price_asc_decreased_radius(
        self,
        app: FastAPI,
        client: AsyncClient,
        cache: "Redis",
        test_products_test_store_1: list[ProductInDB],
        test_products_test_store_2: list[ProductInDB]
    ) -> None:
        params = {
            "lat": 38,
            "lng": 23.8,
            "max_dist": 1,
            "min_price": 0.0,
            "max_price": 5.0,
            "sort_by": "price",
            "sort_order": "ASC",
            "tag_ids": [1],
            "menu_category_ids": [1]
        }
        res = await client.get(
            app.url_path_for("filter-products-from-nearby-stores"),
            params=params
        )
        assert res.status_code == status.HTTP_200_OK

        products_by_menu_categories = \
            res.json().get("products_by_menu_categories")
        
        c = products_by_menu_categories[0]["products"][0]
        assert c["name"] == "test_product_c"


    async def test_filter_single_menu_category_order_view_count_desc(
        self,
        app: FastAPI,
        client: AsyncClient,
        cache: "Redis",
        test_products_test_store_1: list[ProductInDB],
        test_products_test_store_2: list[ProductInDB]
    ) -> None:
        params = {
            "lat": 38,
            "lng": 23.8,
            "max_dist": 5,
            "min_price": 0.0,
            "max_price": 5.0,
            "sort_by": "view_count",
            "sort_order": "DESC",
            "tag_ids": [1],
            "menu_category_ids": [1]
        }
        res = await client.get(
            app.url_path_for("filter-products-from-nearby-stores"),
            params=params
        )
        assert res.status_code == status.HTTP_200_OK

        products_by_menu_categories = \
            res.json().get("products_by_menu_categories")
        
        c, a = products_by_menu_categories[0]["products"]
        assert c["name"] == "test_product_c"
        assert a["name"] == "test_product_a"

    async def test_filter_two_menu_categories_order_price_asc(
        self,
        app: FastAPI,
        client: AsyncClient,
        cache: "Redis",
        test_products_test_store_1: list[ProductInDB],
        test_products_test_store_2: list[ProductInDB]
    ) -> None:
        params = {
            "lat": 38,
            "lng": 23.8,
            "max_dist": 5,
            "min_price": 0.0,
            "max_price": 10.0,
            "sort_by": "price",
            "sort_order": "ASC",
            "tag_ids": [1, 2],
            "menu_category_ids": [1, 2]
        }
        res = await client.get(
            app.url_path_for("filter-products-from-nearby-stores"),
            params=params
        )
        assert res.status_code == status.HTTP_200_OK

        products_by_menu_categories = \
            res.json().get("products_by_menu_categories")
        
        a, c = products_by_menu_categories[0]["products"]
        assert a["name"] == "test_product_a"
        assert c["name"] == "test_product_c"

        a = products_by_menu_categories[1]["products"][0]
        assert a["name"] == "test_product_a"

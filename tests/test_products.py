import pytest
from typing import List
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.products import ProductCreate, ProductInDB, ProductPublic


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestGetProduct:
    async def test_get_product_by_id_successfully(
        self, app: FastAPI, client: AsyncClient, test_product: ProductInDB
    ) -> None:
        res = await client.get(
            app.url_path_for("get-product-by-id", id=test_product.id)
        )
        assert res.status_code == status.HTTP_200_OK

        product = res.json()
        assert product == test_product.model_dump()


    @pytest.mark.parametrize(
        "id, status_code",
        (
            (500, 404),
            (-1, 422),
            (None, 422),
        ),
    )
    async def test_get_product_by_id_invalid_input(
        self, app: FastAPI, client: AsyncClient,
        id: int, status_code: int
    ) -> None:
        res = await client.get(app.url_path_for("get-product-by-id", id=id))
        assert res.status_code == status_code

    async def test_get_all_products_successfully(
        self, app: FastAPI, client: AsyncClient, test_product: ProductInDB
    ) -> None:
        res = await client.get(app.url_path_for("get-all-products"))  
        assert res.status_code == status.HTTP_200_OK
        assert isinstance(res.json(), list)

        products = res.json()
        assert test_product.model_dump() in products


class TestCreateProduct:
    @pytest.fixture
    def new_product(self):
        return ProductCreate(
            name="test product",
            description="test description",
            price=1.00,
        )


    async def test_create_product_successfully(
        self, app: FastAPI, client: AsyncClient, new_product: ProductCreate
    ) -> None:
        res = await client.post(
            app.url_path_for("create-product"), 
            json={"new_product": new_product.model_dump()}
        )
        assert res.status_code == status.HTTP_201_CREATED

        created_product = ProductCreate(**res.json())
        assert created_product == new_product


    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
            (None, 422),
            ({}, 422),
            ({"name": "test_name"}, 422),
            ({"price": 10.00}, 422),
            ({"name": "test_name", "description": "test desc"}, 422),
        ),
    )
    async def test_create_product_invalid_input(
        self, app: FastAPI, client: AsyncClient, 
        invalid_payload: dict, status_code: int
    ) -> None:
        res = await client.post(
            app.url_path_for("create-product"), 
            json={"new_product": invalid_payload}
        )
        assert res.status_code == status_code


class TestUpdateProduct:
    @pytest.mark.parametrize(
        "attrs_to_change, values",
        (
            (["name"], ["new fake product name"]),
            (["description"], ["new fake product desc"]),
            (["price"], [3.14]),
            (
                ["name", "description"],
                [
                    "extra new fake product name",
                    "extra new fake product desc",
                ],
            ),
            (["name", "price"], ["new fake product name", 42.00]),
        ),
    )
    async def test_update_product_by_id_successfully(
        self, app: FastAPI, client: AsyncClient, test_product: ProductInDB,
        attrs_to_change: List[str], values: List[str],
    ) -> None:
        product_update = {
            "product_update": {
                attrs_to_change[i]: values[i] for i in range(len(attrs_to_change))
            }
        }

        res = await client.put(
            app.url_path_for(
                "update-product-by-id",
                id=test_product.id,
            ),
            json=product_update
        )
        assert res.status_code == status.HTTP_200_OK

        # make sure it's the same product
        updated_product = res.json()
        assert updated_product["id"] == test_product.id

        # make sure that any attribute we updated has changed to the correct value
        for i in range(len(attrs_to_change)):
            attr_to_change = updated_product[attrs_to_change[i]]
            assert attr_to_change != test_product.model_dump()[attrs_to_change[i]]
            assert attr_to_change == values[i]

        # make sure that no other attributes' values have changed
        for attr, value in updated_product.items():
            if attr not in attrs_to_change:
                assert test_product.model_dump()[attr] == value


    @pytest.mark.parametrize(
        "id, payload, status_code",
        (
            (-1, {"name": "test"}, 422),
            (0, {"name": "test2"}, 422),
            (1, None, 422),
            (500, {"name": "test3"}, 404),
        ),
    )
    async def test_update_product_by_id_invalid_input(
        self, app: FastAPI, client: AsyncClient,
        id: int, payload: dict, status_code: int,
    ) -> None:
        product_update = {"product_update": payload}

        res = await client.put(
            app.url_path_for("update-product-by-id", id=id),
            json=product_update
        )
        assert res.status_code == status_code


class TestDeleteProduct:
    async def test_delete_product_by_id_successfully(
        self, app: FastAPI, client: AsyncClient, test_product: ProductInDB,
    ) -> None:
        res = await client.delete(
            app.url_path_for(
                "delete-product-by-id",
                id=test_product.id,
            ),
        )
        assert res.status_code == status.HTTP_200_OK

        res = await client.get(
            app.url_path_for(
                "get-product-by-id",
                id=test_product.id,
            ),
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND


    @pytest.mark.parametrize(
        "id, status_code",
        (
            (500, 404),
            (0, 422),
            (-1, 422),
            (None, 422),
        ),
    )
    async def test_delete_product_by_id_invalid_input(
        self, app: FastAPI, client: AsyncClient, test_product: ProductInDB,
        id: int, status_code: int,
    ) -> None:
        res = await client.delete(
            app.url_path_for("delete-product-by-id", id=id),
        )
        assert res.status_code == status_code

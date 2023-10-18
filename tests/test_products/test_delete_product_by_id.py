import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.products import ProductInDB
from app.models.product_details import ProductDetailsInDB
from app.models.store_profiles import StoreProfileInDB
from app.models.product_tags import ProductTagInDB
from app.models.product_menu_categories import ProductMenuCategoryInDB
from app.db.repositories.products import ProductsRepository
from app.db.repositories.product_details import ProductDetailsRepository
from app.db.repositories.product_tags import ProductTagsRepository
from app.db.repositories.product_menu_categories import ProductMenuCategoriesRepository
from fixtures.test_products_fixtures import (
    test_product,
    test_product_details,
    test_product_tags,
    test_product_menu_categories,
    verified_test_store_with_products,
    verified_test_store_with_products_profile,
    authorized_client_for_verified_test_store_with_products
)


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestGetDeleteById:
    async def test_unauthorized_store_cannot_delete_product(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_product: ProductInDB
    ) -> None:
        res = await client.delete(
            app.url_path_for("delete-product-by-id", id=test_product.id)
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


    async def test_authorized_store_fails_to_delete_product_that_does_not_exist(
        self,
        app: FastAPI,
        authorized_client_for_verified_test_store_with_products: AsyncClient,
        test_product: ProductInDB
    ) -> None:
        res = await authorized_client_for_verified_test_store_with_products.delete(
            app.url_path_for("delete-product-by-id", id=500)
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND


    async def test_authorized_store_cannot_delete_product_owned_by_other_store(
        self,
        app: FastAPI,
        authorized_client_for_verified_test_store: AsyncClient,
        test_product: ProductInDB # belongs to verified_test_store_with_products
    ) -> None:
        res = await authorized_client_for_verified_test_store.delete(
            app.url_path_for("delete-product-by-id", id=test_product.id)
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN


    async def test_authorized_store_can_delete_product_successfully(
        self,
        app: FastAPI,
        authorized_client_for_verified_test_store_with_products: AsyncClient,
        test_product: ProductInDB,
        product_repo: ProductsRepository,
        test_product_details: ProductDetailsInDB,
        product_details_repo: ProductDetailsRepository,
        test_product_tags: list[ProductTagInDB],
        product_tag_repo: ProductTagsRepository,
        test_product_menu_categories: list[ProductMenuCategoryInDB],
        product_menu_category_repo: ProductMenuCategoriesRepository
    ) -> None:
        res = await authorized_client_for_verified_test_store_with_products.delete(
            app.url_path_for("delete-product-by-id", id=test_product.id)
        )
        assert res.status_code == status.HTTP_204_NO_CONTENT

        db_product = await product_repo.get_product_by_id(id=test_product.id)
        assert db_product is None

        db_product_details = await product_details_repo.get_product_details_by_product_id(
            product_id=test_product.id
        )
        assert db_product_details is None

        db_product_tags = await product_tag_repo.get_product_tags_by_product_id(
            product_id=test_product.id
        )
        assert len(db_product_tags) == 0

        db_product_menu_categories = await product_menu_category_repo.get_product_menu_categories_by_product_id(
            product_id=test_product.id
        )
        assert len(db_product_menu_categories) == 0

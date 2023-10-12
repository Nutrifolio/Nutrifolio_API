import pytest
from typing import List
from fastapi import FastAPI, status
from httpx import AsyncClient
from app.models.stores import StoreInDB
from app.models.products import ProductCreate, ProductInDB, ProductPublic
from app.db.repositories.products import ProductsRepository
from app.db.repositories.product_details import ProductDetailsRepository
from app.db.repositories.product_tags import ProductTagsRepository
from app.db.repositories.product_menu_categories import ProductMenuCategoriesRepository
from databases import Database


#  Decorates all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio


class TestCreateProduct:
    @pytest.fixture
    def product_repo(self, db: Database) -> ProductsRepository:
        return ProductsRepository(db)

    @pytest.fixture
    def product_details_repo(self, db: Database) -> ProductDetailsRepository:
        return ProductDetailsRepository(db)

    @pytest.fixture
    def product_tag_repo(self, db: Database) -> ProductTagsRepository:
        return ProductTagsRepository(db)
    
    @pytest.fixture
    def product_menu_category_repo(self, db: Database) -> ProductMenuCategoriesRepository:
        return ProductMenuCategoriesRepository(db)


    async def test_unauthorized_store_cannot_create_product(
        self,
        app: FastAPI,
        client: AsyncClient
    ) -> None:
        data = {
            "name": "test product",
            "description": "test description",
            "price": 1.00,
            "is_public": True,
            "calories": 100,
            "protein": 10,
            "carbs": 10,
            "fat": 10,
            "tag_ids": [1, 2],
            "menu_category_ids": [1]
        }

        res = await client.post(
            app.url_path_for("create-product"),
            data=data
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


    async def test_authorized_store_can_create_product_without_logo_with_details(
        self,
        app: FastAPI,
        authorized_client_for_verified_test_store: AsyncClient,
        verified_test_store: StoreInDB,
        product_repo: ProductsRepository,
        product_details_repo: ProductDetailsRepository,
        product_tag_repo: ProductTagsRepository,
        product_menu_category_repo: ProductMenuCategoriesRepository
    ) -> None:
        data = {
            "name": "test product",
            "description": "test description",
            "price": 1.00,
            "is_public": True,
            "calories": 100,
            "protein": 10,
            "carbs": 10,
            "fat": 10,
            "tag_ids": [1, 2],
            "menu_category_ids": [1]
        }

        db_product = await product_repo.get_product_by_name_and_store_id(
            name=data["name"], store_id=verified_test_store.id
        )
        assert db_product is None

        res = await authorized_client_for_verified_test_store.post(
            app.url_path_for("create-product"),
            data=data
        )
        assert res.status_code == status.HTTP_201_CREATED

        db_product = await product_repo.get_product_by_name_and_store_id(
            name=data["name"], store_id=verified_test_store.id
        )
        assert db_product is not None
        assert db_product.name == data["name"]
        assert db_product.description == data["description"]
        assert db_product.image_url is None
        assert db_product.price == data["price"]
        assert db_product.is_public == data["is_public"]
        assert db_product.has_details == True
        assert db_product.store_id == verified_test_store.id

        db_product_details = await product_details_repo.get_product_details_by_product_id(
            product_id=db_product.id
        )
        assert db_product_details is not None
        assert db_product_details.calories == data["calories"]
        assert db_product_details.protein == data["protein"]
        assert db_product_details.carbs == data["carbs"]
        assert db_product_details.fiber is None
        assert db_product_details.sugars is None
        assert db_product_details.fat == data["fat"]
        assert db_product_details.saturated_fat is None

        db_product_tags = await product_tag_repo.get_product_tags_by_product_id(
            product_id=db_product.id
        )
        assert len(db_product_tags) == len(data["tag_ids"])

        db_product_menu_categories = await product_menu_category_repo.get_product_menu_categories_by_product_id(
            product_id=db_product.id
        )
        assert len(db_product_menu_categories) == len(data["menu_category_ids"])


    async def test_authorized_store_can_create_product_with_logo_without_details(
        self,
        app: FastAPI,
        authorized_client_for_verified_test_store: AsyncClient,
        verified_test_store: StoreInDB,
        product_repo: ProductsRepository,
        product_details_repo: ProductDetailsRepository,
        product_tag_repo: ProductTagsRepository,
        product_menu_category_repo: ProductMenuCategoriesRepository,
        mock_sb_client
    ) -> None:
        data = {
            "name": "test product",
            "description": "test description",
            "price": 1.00,
            "is_public": True,
            "tag_ids": [1, 2],
            "menu_category_ids": [1]
        }
        files = {"product_image": open("./tests/assets/Nutrifolio-logo.png", "rb")}

        db_product = await product_repo.get_product_by_name_and_store_id(
            name=data["name"], store_id=verified_test_store.id
        )
        assert db_product is None

        res = await authorized_client_for_verified_test_store.post(
            app.url_path_for("create-product"),
            data=data,
            files=files
        )
        assert res.status_code == status.HTTP_201_CREATED

        db_product = await product_repo.get_product_by_name_and_store_id(
            name=data["name"], store_id=verified_test_store.id
        )
        assert db_product is not None
        assert db_product.name == data["name"]
        assert db_product.description == data["description"]
        assert data["name"] in db_product.image_url
        assert db_product.price == data["price"]
        assert db_product.is_public == data["is_public"]
        assert db_product.has_details == False
        assert db_product.store_id == verified_test_store.id

        db_product_details = await product_details_repo.get_product_details_by_product_id(
            product_id=db_product.id
        )
        assert db_product_details is not None
        assert db_product_details.calories is None
        assert db_product_details.protein is None
        assert db_product_details.carbs is None
        assert db_product_details.fiber is None
        assert db_product_details.sugars is None
        assert db_product_details.fat is None
        assert db_product_details.saturated_fat is None

        db_product_tags = await product_tag_repo.get_product_tags_by_product_id(
            product_id=db_product.id
        )
        assert len(db_product_tags) == len(data["tag_ids"])

        db_product_menu_categories = await product_menu_category_repo.get_product_menu_categories_by_product_id(
            product_id=db_product.id
        )
        assert len(db_product_menu_categories) == len(data["menu_category_ids"])


    async def test_same_store_cannot_create_two_products_with_same_name(
        self,
        app: FastAPI,
        authorized_client_for_verified_test_store: AsyncClient,
        verified_test_store: StoreInDB,
        test_product: ProductInDB,
        product_repo: ProductsRepository
    ) -> None:
        data = {
            "name": "test product",
            "description": "test description",
            "price": 1.00,
            "is_public": True,
            "calories": 100,
            "protein": 10,
            "carbs": 10,
            "fat": 10,
            "tag_ids": [1, 2],
            "menu_category_ids": [1]
        }

        db_product = await product_repo.get_product_by_name_and_store_id(
            name=data["name"], store_id=verified_test_store.id
        )
        assert db_product is not None

        res = await authorized_client_for_verified_test_store.post(
            app.url_path_for("create-product"),
            data=data
        )
        assert res.status_code == status.HTTP_409_CONFLICT

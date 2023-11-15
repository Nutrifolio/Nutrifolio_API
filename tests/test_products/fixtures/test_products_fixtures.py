import pytest
import pytest_asyncio
from httpx import AsyncClient
from databases import Database
from app.models.stores import StoreCreate, StoreInDB
from app.models.store_profiles import StoreProfileCreate, StoreProfileInDB
from app.models.products import ProductCreate, ProductInDB
from app.models.product_details import ProductDetailsCreate, ProductDetailsInDB
from app.models.product_tags import ProductTagCreate, ProductTagInDB
from app.models.product_menu_categories import ProductMenuCategoryCreate, ProductMenuCategoryInDB
from app.db.repositories.stores import StoresRepository
from app.db.repositories.store_profiles import StoreProfilesRepository
from app.db.repositories.products import ProductsRepository
from app.db.repositories.product_details import ProductDetailsRepository
from app.db.repositories.product_tags import ProductTagsRepository
from app.db.repositories.product_menu_categories import ProductMenuCategoriesRepository
from app.services import auth_service
from app.core.config import SECRET_KEY


@pytest_asyncio.fixture
async def verified_test_store_with_products(
    db: Database, store_repo: StoresRepository
) -> StoreInDB:
    new_store = StoreCreate(
        email="store@mystore.com",
        password="mysecretpassword",
        conf_password="mysecretpassword",
    )

    db_new_store = await store_repo.register_new_store(new_store=new_store)

    return await db.fetch_one(
        query="""
            UPDATE stores
            SET is_verified = TRUE
            WHERE id = :id
            RETURNING id, email, password, is_verified;
        """,
        values={"id": db_new_store.id}
    )


@pytest_asyncio.fixture
async def verified_test_store_with_products_profile(
    verified_test_store_with_products: StoreInDB,
    store_profile_repo: StoreProfilesRepository
) -> StoreProfileInDB:
    new_store_profile = StoreProfileCreate(
        name="verified_test_store_with_products_profile",
        description="test_desc",
        phone_number=6943444546,
        address="test_address",
        lat=38.214,
        lng=23.812,
        store_id=verified_test_store_with_products.id
    )

    return await store_profile_repo.create_new_store_profile(
        new_store_profile=new_store_profile
    )


@pytest.fixture
def authorized_client_for_verified_test_store_with_products(
    client: AsyncClient, verified_test_store_with_products: StoreInDB
) -> AsyncClient:
    access_token = auth_service.create_access_token_for_store(
        store_id=verified_test_store_with_products.id,
        secret_key=str(SECRET_KEY)
    )
 
    client.headers = {
        **client.headers,
        "Authorization": f"bearer {access_token}",
    }
 
    return client


@pytest_asyncio.fixture
async def test_product(
    verified_test_store_with_products_profile: StoreProfileInDB,
    product_repo: ProductsRepository
) -> ProductInDB:
    new_product = ProductCreate(
        name="test_product",
        description="test_description",
        price=2.29,
        has_details=True,
        is_public=True,
        store_id=verified_test_store_with_products_profile.store_id
    )

    return await product_repo.create_product(new_product=new_product)


@pytest_asyncio.fixture
async def test_product_details(
    test_product: ProductInDB,
    product_details_repo: ProductDetailsRepository
) -> ProductDetailsInDB:
    new_product_details = ProductDetailsCreate(
        calories=400,
        protein=22.6,
        carbs=43.1,
        fat=11.2,
        product_id=test_product.id
    )

    return await product_details_repo.create_product_details(
        new_product_details=new_product_details
    )


@pytest_asyncio.fixture
async def test_product_tags(
    test_product: ProductInDB,
    product_tag_repo: ProductTagsRepository
) -> list[ProductTagInDB]:
    tag_1 = await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=test_product.id, tag_id=1
        )
    )
    tag_2 = await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=test_product.id, tag_id=2
        )
    )
    tag_3 = await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=test_product.id, tag_id=4
        )
    )
    return [tag_1, tag_2, tag_3]


@pytest_asyncio.fixture
async def test_product_menu_categories(
    test_product: ProductInDB,
    product_menu_category_repo: ProductMenuCategoriesRepository
) -> list[ProductMenuCategoryInDB]:
    menu_categ_1 = await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=test_product.id, menu_category_id=1
        )
    )
    menu_categ_2 = await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=test_product.id, menu_category_id=2
        )
    )
    return [menu_categ_1, menu_categ_2]

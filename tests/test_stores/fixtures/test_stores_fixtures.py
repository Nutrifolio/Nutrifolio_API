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
async def verified_test_store(
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
async def verified_test_store_profile(
    verified_test_store: StoreInDB,
    store_profile_repo: StoreProfilesRepository
) -> StoreProfileInDB:
    new_store_profile = StoreProfileCreate(
        name="verified_test_store_profile",
        description="test_desc",
        phone_number=6943444546,
        address="test_address",
        lat=38.214,
        lng=23.812,
        store_id=verified_test_store.id
    )

    return await store_profile_repo.create_new_store_profile(
        new_store_profile=new_store_profile
    )


@pytest_asyncio.fixture
async def test_product_1(
    verified_test_store_with_products_profile: StoreProfileInDB,
    product_repo: ProductsRepository
) -> ProductInDB:
    new_product = ProductCreate(
        name="test_product_1",
        description="test_description",
        price=2.29,
        has_details=True,
        is_public=True,
        store_id=verified_test_store_with_products_profile.store_id
    )

    return await product_repo.create_product(new_product=new_product)


@pytest_asyncio.fixture
async def test_product_1_tags(
    test_product_1: ProductInDB,
    product_tag_repo: ProductTagsRepository
) -> list[ProductTagInDB]:
    tag_1 = await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=test_product_1.id, tag_id=1
        )
    )
    tag_2 = await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=test_product_1.id, tag_id=2
        )
    )
    tag_3 = await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=test_product_1.id, tag_id=4
        )
    )
    return [tag_1, tag_2, tag_3]


@pytest_asyncio.fixture
async def test_product_1_menu_categories(
    test_product_1: ProductInDB,
    product_menu_category_repo: ProductMenuCategoriesRepository
) -> list[ProductMenuCategoryInDB]:
    menu_categ_1 = await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=test_product_1.id, menu_category_id=1
        )
    )
    menu_categ_2 = await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=test_product_1.id, menu_category_id=2
        )
    )
    return [menu_categ_1, menu_categ_2]


@pytest_asyncio.fixture
async def test_product_2(
    verified_test_store_with_products_profile: StoreProfileInDB,
    product_repo: ProductsRepository
) -> ProductInDB:
    new_product = ProductCreate(
        name="test_product_2",
        description="test_description",
        price=3.49,
        has_details=False,
        is_public=True,
        store_id=verified_test_store_with_products_profile.store_id
    )

    return await product_repo.create_product(new_product=new_product)


@pytest_asyncio.fixture
async def test_product_2_tags(
    test_product_2: ProductInDB,
    product_tag_repo: ProductTagsRepository
) -> list[ProductTagInDB]:
    tag_1 = await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=test_product_2.id, tag_id=1
        )
    )
    tag_2 = await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=test_product_2.id, tag_id=3
        )
    )
    return [tag_1, tag_2]


@pytest_asyncio.fixture
async def test_product_2_menu_categories(
    test_product_2: ProductInDB,
    product_menu_category_repo: ProductMenuCategoriesRepository
) -> list[ProductMenuCategoryInDB]:
    menu_categ_1 = await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=test_product_2.id, menu_category_id=1
        )
    )
    return [menu_categ_1]


@pytest_asyncio.fixture
async def test_products(
    db: Database,
    verified_test_store_profile: StoreProfileInDB,
    product_repo: ProductsRepository,
    product_tag_repo: ProductTagsRepository,
    product_menu_category_repo: ProductMenuCategoriesRepository
) -> list[ProductInDB]:
    new_product = ProductCreate(
        name="test_product_1",
        description="test_description",
        price=2.29,
        has_details=True,
        is_public=True,
        store_id=verified_test_store_profile.store_id
    )
    product_1 = await product_repo.create_product(new_product=new_product)

    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=product_1.id, tag_id=1
        )
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=product_1.id, tag_id=2
        )
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=product_1.id, tag_id=4
        )
    )
    await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=product_1.id, menu_category_id=1
        )
    )
    await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=product_1.id, menu_category_id=2
        )
    )

    new_product = ProductCreate(
        name="test_product_2",
        description="test_description",
        price=3.49,
        has_details=False,
        is_public=True,
        store_id=verified_test_store_profile.store_id
    )
    product_2 = await product_repo.create_product(new_product=new_product)

    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=product_2.id, tag_id=1
        )
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=product_2.id, tag_id=3
        )
    )
    await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=product_2.id, menu_category_id=1
        )
    )

    return [product_1, product_2]

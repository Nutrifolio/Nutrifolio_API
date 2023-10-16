import pytest_asyncio
from databases import Database
from app.models.products import ProductCreate, ProductInDB
from app.db.repositories.products import ProductsRepository
from app.models.stores import StoreCreate, StoreInDB
from app.db.repositories.stores import StoresRepository
from app.models.store_profiles import StoreProfileCreate, StoreProfileInDB
from app.db.repositories.store_profiles import StoreProfilesRepository
from app.models.product_tags import ProductTagCreate
from app.db.repositories.product_tags import ProductTagsRepository
from app.models.product_menu_categories import ProductMenuCategoryCreate
from app.db.repositories.product_menu_categories import ProductMenuCategoriesRepository


'''
The data being used to test the filtering functionality in SQL:

INSERT INTO stores (id, email, password)
VALUES
    (1, 'test_store_1@mystore.com', 'mysecretpassword'),
    (2, 'test_store_2@mystore.com', 'mysecretpassword');

INSERT INTO store_profiles (id, name, address, lat, lng, location, store_id)
VALUES
    (1, 'test_store_1', 'test_address', 38.0093, 23.8264, ST_MakePoint(23.8264, 38.0093)::geography, 1),
    (2, 'test_store_2', 'test_address', 38.0073, 23.7993, ST_MakePoint(23.7993, 38.0073)::geography, 2);

INSERT INTO products (id, name, price, view_count, has_details, is_public, store_id)
VALUES
    (1, 'test_product_a', 1.29, 3, FALSE, TRUE, 1),
    (2, 'test_product_b', 5.49, 6, FALSE, TRUE, 1),
    (3, 'test_product_c', 2.89, 9, FALSE, TRUE, 2),
    (4, 'test_product_d', 2.49, 2, FALSE, FALSE, 2);

INSERT INTO product_tags (product_id, tag_id)
VALUES
    (1, 1), (1, 2), (1, 4),
    (2, 1), (2, 3),
    (3, 1), (3, 2), (3, 5),
    (4, 1), (4, 2), (4, 3);

INSERT INTO product_menu_categories (product_id, menu_category_id)
VALUES
    (1, 1), (1, 2),
    (2, 1),
    (3, 1),
    (4, 1), (4, 2);
'''


@pytest_asyncio.fixture
async def test_store_1(store_repo: StoresRepository) -> StoreInDB:
    new_store = StoreCreate(
        email="test_store_1@mystore.com",
        password="mysecretpassword",
        conf_password="mysecretpassword",
    )

    return await store_repo.register_new_store(new_store=new_store)


@pytest_asyncio.fixture
async def test_store_2(store_repo: StoresRepository) -> StoreInDB:
    new_store = StoreCreate(
        email="test_store_2@mystore.com",
        password="mysecretpassword",
        conf_password="mysecretpassword",
    )

    return await store_repo.register_new_store(new_store=new_store)


@pytest_asyncio.fixture
async def test_store_1_profile(
    test_store_1: StoreInDB,
    store_profile_repo: StoreProfilesRepository
) -> StoreInDB:
    new_store_profile = StoreProfileCreate(
        name="test_store_1",
        description="test_desc",
        phone_number=6943444546,
        address="test_address",
        lat=38.0093,
        lng=23.8264,
        store_id=test_store_1.id
    )

    return await store_profile_repo.create_new_store_profile(
        new_store_profile=new_store_profile
    )


@pytest_asyncio.fixture
async def test_store_2_profile(
    test_store_2: StoreInDB,
    store_profile_repo: StoreProfilesRepository
) -> StoreInDB:
    new_store_profile = StoreProfileCreate(
        name="test_store_2",
        description="test_desc",
        phone_number=6943444546,
        address="test_address",
        lat=38.0073,
        lng=23.7993,
        store_id=test_store_2.id
    )

    return await store_profile_repo.create_new_store_profile(
        new_store_profile=new_store_profile
    )


@pytest_asyncio.fixture
async def test_products_test_store_1(
    db: Database,
    test_store_1_profile: StoreProfileInDB,
    product_repo: ProductsRepository,
    product_tag_repo: ProductTagsRepository,
    product_menu_category_repo: ProductMenuCategoriesRepository
) -> list[ProductInDB]:
    new_product = ProductCreate(
        name="test_product_a",
        description="test description 1",
        price=1.29,
        has_details=False,
        is_public=True,
        store_id=test_store_1_profile.id
    )

    db_test_product_a = await product_repo.create_product(new_product=new_product)
    updated_product_a = await db.fetch_one(
        query="""
            UPDATE products
            SET view_count = 3
            WHERE id = :id
            RETURNING
                id, name, description, image_url, price,
                view_count, has_details, is_public, store_id;
        """,
        values={"id": db_test_product_a.id}
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=updated_product_a.id, tag_id=1
        )
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=updated_product_a.id, tag_id=2
        )
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=updated_product_a.id, tag_id=4
        )
    )
    await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=updated_product_a.id, menu_category_id=1
        )
    )
    await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=updated_product_a.id, menu_category_id=2
        )
    )

    new_product = ProductCreate(
        name="test_product_b",
        description="test description 2",
        price=5.49,
        has_details=False,
        is_public=True,
        store_id=test_store_1_profile.id
    )

    db_test_product_b = await product_repo.create_product(new_product=new_product)
    updated_product_b = await db.fetch_one(
        query="""
            UPDATE products
            SET view_count = 6
            WHERE id = :id
            RETURNING
                id, name, description, image_url, price,
                view_count, has_details, is_public, store_id;
        """,
        values={"id": db_test_product_b.id}
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=updated_product_b.id, tag_id=1
        )
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=updated_product_b.id, tag_id=3
        )
    )
    await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=updated_product_b.id, menu_category_id=1
        )
    )

    return [updated_product_a, updated_product_b]


@pytest_asyncio.fixture
async def test_products_test_store_2(
    db: Database,
    test_store_2_profile: StoreProfileInDB,
    product_repo: ProductsRepository,
    product_tag_repo: ProductTagsRepository,
    product_menu_category_repo: ProductMenuCategoriesRepository
) -> list[ProductInDB]:
    new_product = ProductCreate(
        name="test_product_c",
        description="test description 3",
        price=2.89,
        has_details=False,
        is_public=True,
        store_id=test_store_2_profile.id
    )

    db_test_product_c = await product_repo.create_product(new_product=new_product)
    updated_product_c = await db.fetch_one(
        query="""
            UPDATE products
            SET view_count = 9
            WHERE id = :id
            RETURNING
                id, name, description, image_url, price,
                view_count, has_details, is_public, store_id;
        """,
        values={"id": db_test_product_c.id}
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=updated_product_c.id, tag_id=1
        )
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=updated_product_c.id, tag_id=2
        )
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=updated_product_c.id, tag_id=5
        )
    )
    await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=updated_product_c.id, menu_category_id=1
        )
    )

    new_product = ProductCreate(
        name="test_product_d",
        description="test description 4",
        price=2.49,
        has_details=False,
        is_public=False,
        store_id=test_store_2_profile.id
    )

    db_test_product_d = await product_repo.create_product(new_product=new_product)
    updated_product_d = await db.fetch_one(
        query="""
            UPDATE products
            SET view_count = 2
            WHERE id = :id
            RETURNING
                id, name, description, image_url, price,
                view_count, has_details, is_public, store_id;
        """,
        values={"id": db_test_product_d.id}
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=updated_product_d.id, tag_id=1
        )
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=updated_product_d.id, tag_id=2
        )
    )
    await product_tag_repo.create_product_tag(
        new_product_tag=ProductTagCreate(
            product_id=updated_product_d.id, tag_id=3
        )
    )
    await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=updated_product_d.id, menu_category_id=1
        )
    )
    await product_menu_category_repo.create_product_menu_category(
        new_product_menu_category=ProductMenuCategoryCreate(
            product_id=updated_product_d.id, menu_category_id=2
        )
    )

    return [updated_product_c, updated_product_d]

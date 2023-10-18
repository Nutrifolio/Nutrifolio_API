import pytest_asyncio
from app.models.stores import StoreInDB
from app.models.products import ProductCreate, ProductInDB
from app.models.product_details import ProductDetailsCreate, ProductDetailsInDB
from app.models.product_tags import ProductTagCreate, ProductTagInDB
from app.models.product_menu_categories import ProductMenuCategoryCreate, ProductMenuCategoryInDB
from app.db.repositories.products import ProductsRepository
from app.db.repositories.product_details import ProductDetailsRepository
from app.db.repositories.product_tags import ProductTagsRepository
from app.db.repositories.product_menu_categories import ProductMenuCategoriesRepository


@pytest_asyncio.fixture
async def test_product(
    test_store_profile: StoreInDB,
    product_repo: ProductsRepository
) -> ProductInDB:
    new_product = ProductCreate(
        name="test_product",
        description="test_description",
        price=2.29,
        has_details=True,
        is_public=True,
        store_id=test_store_profile.store_id
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

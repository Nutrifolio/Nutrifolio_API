import copy
import itertools
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Query
from app.models.products import Filters, FilterOut
from app.db.repositories.store_profiles import StoreProfilesRepository
from app.db.repositories.products import ProductsRepository
from app.db.repositories.tags import TagsRepository
from app.db.repositories.menu_categories import MenuCategoriesRepository
from app.api.dependencies.database import get_database, get_repository
from app.api.dependencies.cache import get_cache
from app.api.enums.products import MaxDistanceOption, SortByOption, SortOrderOption
from . import router, products_logger


def create_separate_product_for_each_matching_menu_category(
    menu_categories: list[dict],
    menu_category_ids: list[int],
    product: dict,
    completed_products: list[dict]
) -> None:
    for menu_category in menu_categories:
        if menu_category.id in menu_category_ids:
            product_cp = copy.deepcopy(product)
            product_cp["menu_category"] = menu_category.model_dump()
            completed_products.append(product_cp)


async def attach_related_info_to_products(
    products: list[dict],
    lat: float,
    lng: float,
    menu_category_ids: list[int],
    store_profile_repo: Annotated[
        StoreProfilesRepository, Depends(get_repository(StoreProfilesRepository))
    ],
    tag_repo: Annotated[
        TagsRepository, Depends(get_repository(TagsRepository))
    ],
    menu_category_repo: Annotated[
        MenuCategoriesRepository, 
        Depends(get_repository(MenuCategoriesRepository))
    ]
) -> list[dict]:
    completed_products = []
    for product in products:
        product = product.model_dump()

        product["store"] = await store_profile_repo.get_store_profile_filter_view_by_store_id(
            store_id=product["store_id"],
            lat=lat,
            lng=lng
        )

        product["tags"] = await tag_repo.get_tags_for_product_by_product_id(
            product_id=product["id"]
        )

        menu_categories = await menu_category_repo.get_menu_categories_for_product_by_product_id(
            product_id=product["id"]
        )

        create_separate_product_for_each_matching_menu_category(
            menu_categories=menu_categories,
            menu_category_ids=menu_category_ids,
            product=product,
            completed_products=completed_products
        )
    return completed_products


def group_products_by_menu_category(products: list[dict]) -> list[dict]:
    products_by_menu_categories = []
    products.sort(key=lambda product: product["menu_category"]["id"])
    for key, group in itertools.groupby(
        products, lambda product: product["menu_category"]
    ):
        category_products = []
        for product in group:
            del product["menu_category"]
            category_products.append(product)
        products_by_menu_categories.append(
            {"menu_category": key, "products": category_products}
        )
    return products_by_menu_categories


def sort_products_per_menu_category(
    products_by_menu_categories: list[dict],
    sort_by: SortByOption,
    sort_order: SortOrderOption
) -> None:
    for products_by_menu_category in products_by_menu_categories:
        if sort_by == SortByOption.DISTANCE_KM:
            products_by_menu_category["products"].sort(
                key=lambda product: getattr(product["store"], sort_by.value),
                reverse=sort_order.value == "DESC"
            )
        else:
            products_by_menu_category["products"].sort(
                key=lambda product: product[sort_by.value],
                reverse=sort_order.value == "DESC"
            )


@router.get(
    "/",
    response_model=FilterOut,
    name="filter-products-from-nearby-stores"
)
async def filter_products_from_nearby_stores(
    cache: Annotated["Redis", Depends(get_cache)],
    store_profile_repo: Annotated[
        StoreProfilesRepository, Depends(get_repository(StoreProfilesRepository))
    ],
    products_repo: Annotated[
        ProductsRepository, Depends(get_repository(ProductsRepository))
    ],
    tag_repo: Annotated[
        TagsRepository, Depends(get_repository(TagsRepository))
    ],
    menu_category_repo: Annotated[
        MenuCategoriesRepository,
        Depends(get_repository(MenuCategoriesRepository))
    ],
    lat: Annotated[float, Query(ge=-90, le=90)],
    lng: Annotated[float, Query(ge=-180, le=180)],
    max_dist: MaxDistanceOption,
    min_price: Annotated[float, Query(ge=0)],
    max_price: Annotated[float, Query(gt=0)],
    tag_ids: Annotated[list[int], Query(...)],
    menu_category_ids: Annotated[list[int], Query(...)],
    sort_by: SortByOption,
    sort_order: SortOrderOption
) -> FilterOut:
    try:
        store_ids = await store_profile_repo.get_nearby_store_ids(
            cache=cache,
            lat=lat,
            lng=lng,
            max_dist=max_dist,
        )

        products = await products_repo.filter_products_from_nearby_stores(
            store_ids=store_ids,
            tag_ids=tag_ids,
            menu_category_ids=menu_category_ids,
            min_price=min_price,
            max_price=max_price
        )

        completed_products = await attach_related_info_to_products(
            products=products,
            lat=lat,
            lng=lng,
            menu_category_ids=menu_category_ids,
            store_profile_repo=store_profile_repo,
            tag_repo=tag_repo,
            menu_category_repo=menu_category_repo
        )

        products_by_menu_categories = group_products_by_menu_category(
            completed_products
        )

        sort_products_per_menu_category(
            products_by_menu_categories, sort_by, sort_order
        )

        return {"products_by_menu_categories": products_by_menu_categories}
    except Exception as exc:
        products_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to retrieve products."
        )

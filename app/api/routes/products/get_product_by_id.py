from typing import Annotated
from fastapi import Depends, status, HTTPException, Path
from app.models.products import ProductDetailed, ProductDetailedOut
from app.models.product_details import ProductDetailsOut
from app.models.tags import TagOut
from app.models.menu_categories import MenuCategoryOut
from app.models.store_profiles import StoreProfileOutProductDetailed
from app.db.repositories.products import ProductsRepository
from app.db.repositories.product_details import ProductDetailsRepository
from app.db.repositories.product_tags import ProductTagsRepository
from app.db.repositories.product_menu_categories import ProductMenuCategoriesRepository
from app.db.repositories.tags import TagsRepository
from app.db.repositories.menu_categories import MenuCategoriesRepository
from app.db.repositories.store_profiles import StoreProfilesRepository
from app.api.dependencies.database import get_database, get_repository
from app.api.exceptions.products import ProductNotFound
from . import router, products_logger


@router.get("/{id}", response_model=ProductDetailedOut, name="get-product-by-id")
async def get_product_by_id(
    id: Annotated[int, Path(ge=1)],
    product_repo: Annotated[
        ProductsRepository, Depends(get_repository(ProductsRepository))
    ],
    product_details_repo: Annotated[
        ProductDetailsRepository,
        Depends(get_repository(ProductDetailsRepository))
    ],
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
) -> ProductDetailedOut:
    try:
        db_product = await product_repo.get_product_by_id(id=id)
        if not db_product or not db_product.is_public:
            raise ProductNotFound(f"There is no product with the id of {id}")
        
        await product_repo.increment_product_view_count_by_id(id=id)

        db_product_details = await product_details_repo.get_product_details_by_product_id(
            product_id=db_product.id
        )

        db_store_profile = await store_profile_repo.get_store_profile_simple_view_by_store_id(
            store_id=db_product.store_id
        )

        db_tags = await tag_repo.get_tags_for_product_by_product_id(
            product_id=db_product.id
        )

        db_menu_categories = await menu_category_repo.get_menu_categories_for_product_by_product_id(
            product_id=db_product.id
        )

        return {
            "product": ProductDetailed(
                **db_product.model_dump(),
                store=StoreProfileOutProductDetailed(
                    **db_store_profile.model_dump()
                ),
                details=ProductDetailsOut(
                    **db_product_details.model_dump()
                ),
                tags=[
                    TagOut(**tag.model_dump()) for tag in db_tags
                ],
                menu_categories=[
                    MenuCategoryOut(**menu_category.model_dump())
                    for menu_category in db_menu_categories
                ]
            )
        }
    except ProductNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    except Exception as exc:
        products_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to fetch product."
        )

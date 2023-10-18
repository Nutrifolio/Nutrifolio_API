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
from app.api.dependencies.auth import get_current_store_id
from app.api.exceptions.products import ProductNotFound, ProductBelongsToAnotherStore
from . import router, products_logger


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete-product-by-id"
)
async def delete_product_by_id(
    id: Annotated[int, Path(ge=1)],
    store_id: Annotated[int, Depends(get_current_store_id)],
    product_repo: Annotated[
        ProductsRepository, Depends(get_repository(ProductsRepository))
    ]
) -> None:
    try:
        db_product = await product_repo.get_product_by_id(id=id)
        if not db_product:
            raise ProductNotFound(f"There is no product with the id of {id}")
        
        if db_product.store_id != store_id:
            raise ProductBelongsToAnotherStore(
                f"The product with the id of {id} belongs to another store. You can only delete products that belong to your store."
            )
        
        await product_repo.delete_product_by_id(id=id)
    except ProductNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    except ProductBelongsToAnotherStore as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    except Exception as exc:
        products_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to fetch product."
        )

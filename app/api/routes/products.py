from typing import List, Annotated
from fastapi import APIRouter, Path, Body, Depends, status, HTTPException
from app.models.products import ProductCreate, ProductUpdate, ProductPublic
from app.db.repositories.products import ProductsRepository
from app.api.dependencies.database import get_repository
from app.api.exceptions.products import ProductNotFound
from app.core.logging import get_logger


router = APIRouter()

products_logger = get_logger(__name__)


@router.get("/", response_model=List[ProductPublic], name="get-all-products")
async def get_all_products(
    products_repo: Annotated[ProductsRepository, Depends(get_repository(ProductsRepository))]
) -> List[ProductPublic]:
    try:
        return await products_repo.get_all_products()
    except Exception as exc:
        products_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to retrieve products."
        )


@router.get("/{id}/", response_model=ProductPublic, name="get-product-by-id")
async def get_product_by_id(
    id: Annotated[int, Path(..., ge=1)], 
    products_repo: Annotated[ProductsRepository, Depends(get_repository(ProductsRepository))]
) -> ProductPublic:
    try:
        product = await products_repo.get_product_by_id(id=id)

        if not product:
            raise ProductNotFound(f"No product found with the id={id}")

        return product
    except ProductNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    except Exception as exc:
        products_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to retrieve product."
        )


@router.post("/", response_model=ProductPublic, name="create-product", status_code=status.HTTP_201_CREATED)
async def create_product(
    new_product: Annotated[ProductCreate, Body(..., embed=True)],
    products_repo: Annotated[ProductsRepository, Depends(get_repository(ProductsRepository))],
) -> ProductPublic:
    try:
        return await products_repo.create_product(new_product=new_product)
    except Exception as exc:
        products_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to create product."
        )


@router.put("/{id}/", response_model=ProductPublic, name="update-product-by-id")
async def update_product_by_id(
    id: Annotated[int, Path(..., ge=1)],
    product_update: Annotated[ProductUpdate, Body(..., embed=True)],
    products_repo: Annotated[ProductsRepository, Depends(get_repository(ProductsRepository))],
) -> ProductPublic:
    try:
        updated_product = await products_repo.update_product_by_id(
            id=id, product_update=product_update
        )

        if not updated_product:
            raise ProductNotFound(f"No product found with the id={id}")

        return updated_product
    except ProductNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    except Exception as exc:
        products_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to update product."
        )


@router.delete("/{id}/", response_model=int, name="delete-product-by-id")
async def delete_product_by_id(
    id: Annotated[int, Path(..., ge=1)],
    products_repo: Annotated[ProductsRepository, Depends(get_repository(ProductsRepository))],
) -> int:
    try:
        deleted_id = await products_repo.delete_product_by_id(id=id)

        if not deleted_id:
            raise ProductNotFound(f"No product found with the id={id}")

        return deleted_id
    except ProductNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    except Exception as exc:
        products_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to delete product."
        )

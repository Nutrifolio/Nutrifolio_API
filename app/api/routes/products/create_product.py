from typing import Annotated
from pydantic import ValidationError
from databases import Database
from mypy_boto3_s3.client import S3Client
from fastapi import Depends, status, HTTPException, File, UploadFile, Form
from fastapi.encoders import jsonable_encoder
from app.models.products import ProductCreate, ProductOutCreate
from app.models.product_details import ProductDetailsCreate, ProductDetailsOut
from app.models.product_tags import ProductTagCreate
from app.models.product_menu_categories import ProductMenuCategoryCreate
from app.models.tags import TagOut
from app.models.menu_categories import MenuCategoryOut
from app.db.repositories.products import ProductsRepository
from app.db.repositories.product_details import ProductDetailsRepository
from app.db.repositories.product_tags import ProductTagsRepository
from app.db.repositories.product_menu_categories import ProductMenuCategoriesRepository
from app.db.repositories.tags import TagsRepository
from app.db.repositories.menu_categories import MenuCategoriesRepository
from app.api.dependencies.space_bucket import get_sb_client
from app.api.dependencies.database import get_database, get_repository
from app.api.dependencies.auth import get_current_store_id
from app.api.exceptions.products import DuplicateProductNameForTheSameStore
from app.core.config import DO_SPACE_BUCKET_URL
from . import router, products_logger


async def create_product_tags(
    product_id: int,
    tag_ids: list[int],
    product_tag_repo: ProductTagsRepository,
    tag_repo: TagsRepository,
) -> list[TagOut]:
    tags = []
    for tag_id in tag_ids:
        new_product_tag = ProductTagCreate(
            product_id=product_id,
            tag_id=tag_id,
        )

        await product_tag_repo.create_product_tag(
            new_product_tag=new_product_tag
        )

        tag = await tag_repo.get_tag_by_id(id=tag_id)
        tags.append(TagOut(**tag.model_dump()))
    return tags


async def create_product_menu_categories(
    product_id: int,
    menu_category_ids: list[int],
    product_menu_category_repo: ProductMenuCategoriesRepository,
    menu_category_repo: MenuCategoriesRepository,
) -> list[MenuCategoryOut]:
    menu_categories = []
    for menu_category_id in menu_category_ids:
        new_product_menu_category = ProductMenuCategoryCreate(
            product_id=product_id,
            menu_category_id=menu_category_id,
        )

        await product_menu_category_repo.create_product_menu_category(
            new_product_menu_category=new_product_menu_category
        )

        menu_category = await menu_category_repo.get_menu_category_by_id(id=menu_category_id)
        menu_categories.append(MenuCategoryOut(**menu_category.model_dump()))
    return menu_categories


@router.post(
    "/",
    response_model=ProductOutCreate,
    name="create-product",
    status_code=status.HTTP_201_CREATED
)
async def create_product(
    store_id: Annotated[int, Depends(get_current_store_id)],
    sb_client: Annotated[S3Client, Depends(get_sb_client)],
    db: Annotated[Database, Depends(get_database)],
    product_repo: Annotated[
        ProductsRepository, Depends(get_repository(ProductsRepository))
    ],
    product_details_repo: Annotated[
        ProductDetailsRepository, 
        Depends(get_repository(ProductDetailsRepository))
    ],
    product_tag_repo: Annotated[
        ProductTagsRepository, Depends(get_repository(ProductTagsRepository))
    ],
    product_menu_category_repo: Annotated[
        ProductMenuCategoriesRepository, 
        Depends(get_repository(ProductMenuCategoriesRepository))
    ],
    tag_repo: Annotated[
        TagsRepository, Depends(get_repository(TagsRepository))
    ],
    menu_category_repo: Annotated[
        MenuCategoriesRepository, 
        Depends(get_repository(MenuCategoriesRepository))
    ],
    name: str = Form(...),
    description: str = Form(None),
    product_image: UploadFile = File(None),
    price: float = Form(...),
    is_public: bool = Form(...),
    calories: int = Form(None),
    protein: float = Form(None),
    carbs: float = Form(None),
    fiber: float = Form(None),
    sugars: float = Form(None),
    fat: float = Form(None),
    saturated_fat: float = Form(None),
    tag_ids: list[int] = Form(...),
    menu_category_ids: list[int] = Form(...),
) -> ProductOutCreate:
    try:
        db_product = await product_repo.get_product_by_name_and_store_id(
            name=name, store_id=store_id
        )
        if db_product:
            raise DuplicateProductNameForTheSameStore(f"There is already a product with the name {name} for your store.")

        has_details = False
        if calories and protein and carbs and fat:
            has_details = True

        image_url = None
        if product_image is not None:
            space_bucket_folder = 'products'
            sb_client.upload_fileobj(
                product_image.file,
                space_bucket_folder,
                name,
                ExtraArgs={"ACL": "public-read"}
            )
            image_url = f"{DO_SPACE_BUCKET_URL}/{space_bucket_folder}/{name}"

        async with db.transaction():
            new_product = ProductCreate(
                name=name,
                description=description,
                image_url=image_url,
                price=price,
                has_details=has_details,
                is_public=is_public,
                store_id=store_id,
            )
            created_product = await product_repo.create_product(
                new_product=new_product
            )

            new_product_details = ProductDetailsCreate(
                calories=calories,
                protein=protein,
                carbs=carbs,
                fiber=fiber,
                sugars=sugars,
                fat=fat,
                saturated_fat=saturated_fat,
                product_id=created_product.id,
            )
            created_product_details = await product_details_repo.create_product_details(
                new_product_details=new_product_details
            )

            tags = await create_product_tags(
                product_id=created_product.id,
                tag_ids=tag_ids,
                product_tag_repo=product_tag_repo,
                tag_repo=tag_repo,
            )

            menu_categories = await create_product_menu_categories(
                product_id=created_product.id,
                menu_category_ids=menu_category_ids,
                product_menu_category_repo=product_menu_category_repo,
                menu_category_repo=menu_category_repo,
            )

        return ProductOutCreate(
            id=created_product.id,
            name=created_product.name,
            description=created_product.description,
            image_url=created_product.image_url,
            price=created_product.price,
            is_public=created_product.is_public,
            store_id=created_product.store_id,
            details=ProductDetailsOut(**created_product_details.model_dump()),
            tags=tags,
            menu_categories=menu_categories,
        )
    except ValidationError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=jsonable_encoder(exc.errors()),
        )
    except DuplicateProductNameForTheSameStore as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))
    except Exception as exc:
        products_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Failed to create product."
        )

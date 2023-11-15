import copy
import itertools
from typing import Annotated
from pydantic import ValidationError
from databases import Database
from mypy_boto3_s3.client import S3Client
from fastapi import APIRouter, Path, Body, Depends, status, HTTPException, File, UploadFile, Form
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.services import auth_service
from app.models.core import DetailResponse
from app.models.token import AccessToken
from app.models.stores import StoreCreate, StoreInDB
from app.models.store_profiles import StoreProfileCreate, StoreProfileInDB, StoreProfileOut, StoreProfileOutWithProducts
from app.db.repositories.stores import StoresRepository
from app.db.repositories.store_profiles import StoreProfilesRepository
from app.db.repositories.products import ProductsRepository
from app.db.repositories.tags import TagsRepository
from app.db.repositories.menu_categories import MenuCategoriesRepository
from app.api.dependencies.space_bucket import get_sb_client
from app.api.dependencies.auth import get_current_store_profile
from app.api.dependencies.database import get_database, get_repository
from app.api.exceptions.auth import EmailAlreadyExists, InvalidCredentials
from app.api.exceptions.stores import StoreNameAlreadyExists, StoreNotVerified, StoreNotFound
from app.core.config import DO_SPACE_BUCKET_URL
from app.core.logging import get_logger


router = APIRouter()

stores_logger = get_logger(__name__)


@router.post("/register", response_model=DetailResponse, name="register-new-store", status_code=status.HTTP_201_CREATED)
async def register_new_store(
    sb_client: Annotated[S3Client, Depends(get_sb_client)],
    db: Annotated[Database, Depends(get_database)],
    store_repo: Annotated[StoresRepository, Depends(get_repository(StoresRepository))],
    store_profile_repo: Annotated[StoreProfilesRepository, Depends(get_repository(StoreProfilesRepository))],
    email: str = Form(...),
    password: str = Form(...),
    conf_password: str = Form(...),
    name: str = Form(...),
    desc: str = Form(None),
    logo_image: UploadFile = File(None),
    phone_number: int = Form(None),
    address: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...)
) -> DetailResponse:
    try:
        db_store = await store_repo.get_store_by_email(email=email)
        if db_store:
            raise EmailAlreadyExists(f"There is already an account registered with the email {email}")
        
        db_store_profile = await store_profile_repo.get_store_profile_by_name(name=name)
        if db_store_profile:
            raise StoreNameAlreadyExists(f"There is already an account registered with the name {name}")

        logo_url = None
        if logo_image is not None:
            space_bucket_folder = 'store_profiles'
            sb_client.upload_fileobj(
                logo_image.file,
                space_bucket_folder,
                name,
                ExtraArgs={"ACL": "public-read"}
            )
            logo_url = f"{DO_SPACE_BUCKET_URL}/{space_bucket_folder}/{name}"
        
        async with db.transaction():
            new_store = StoreCreate(
                email=email, password=password, conf_password=conf_password
            )
            created_store = await store_repo.register_new_store(new_store=new_store)

            new_store_profile = StoreProfileCreate(
                name=name,
                desc=desc,
                logo_url=logo_url,
                phone_number=phone_number,
                address=address,
                lat=lat,
                lng=lng,
                store_id=created_store.id,
            )
            created_store_profile = await store_profile_repo.create_new_store_profile(
                new_store_profile=new_store_profile
            )

        return DetailResponse(detail="Successfully submitted for review.")
    except ValidationError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=jsonable_encoder(exc.errors()),
        )
    except EmailAlreadyExists as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))
    except StoreNameAlreadyExists as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))
    except Exception as exc:
        stores_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, 
            "Failed to register store."
        )


@router.post('/login', response_model=AccessToken, name="store-login")
async def store_login(
    store_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    store_repo: Annotated[StoresRepository, Depends(get_repository(StoresRepository))],
) -> AccessToken:
    try:
        # OAuth2PasswordRequestForm's username corresponds to the email
        db_store = await store_repo.get_store_by_email(
            email=store_credentials.username
        )
        if not db_store:
            raise InvalidCredentials("Incorrect email or password.")

        if not auth_service.verify_password(
            password=store_credentials.password,
            hashed_password=db_store.password
        ):
            raise InvalidCredentials("Incorrect email or password.")
        
        if not db_store.is_verified:
            raise StoreNotVerified("Store verification is pending, we will contact you via an email when the process has finished.")

        access_token = auth_service.create_access_token_for_store(
            store_id=db_store.id
        )
        return AccessToken(access_token=access_token, token_type="bearer")
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Basic"}
        )
    except StoreNotVerified as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    except Exception as exc:
        stores_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, 
            "Failed to login."
        )


@router.get("/me", response_model=StoreProfileOut, name="get-current-store-profile-info")
async def get_current_store_info(
    current_store: Annotated[StoreProfileInDB, Depends(get_current_store_profile)]
) -> StoreProfileOut:
    return current_store


def create_separate_product_for_each_menu_category(
    menu_categories: list[dict],
    product: dict,
    completed_products: list[dict]
) -> None:
    for menu_category in menu_categories:
        product_cp = copy.deepcopy(product)
        product_cp["menu_category"] = menu_category.model_dump()
        completed_products.append(product_cp)


async def attach_related_info_to_products(
    products: list[dict],
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

        product["tags"] = await tag_repo.get_tags_for_product_by_product_id(
            product_id=product["id"]
        )

        menu_categories = await menu_category_repo.get_menu_categories_for_product_by_product_id(
            product_id=product["id"]
        )

        create_separate_product_for_each_menu_category(
            menu_categories=menu_categories,
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


@router.get(
    "/{id}",
    response_model=StoreProfileOutWithProducts,
    name="get-store-by-id"
)
async def get_store_by_id(
    id: Annotated[int, Path(ge=1)],
    product_repo: Annotated[
        ProductsRepository, Depends(get_repository(ProductsRepository))
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
) -> StoreProfileOutWithProducts:
    try:
        db_store_profile = await store_profile_repo.get_store_profile_by_store_id(
            store_id=id
        )
        if not db_store_profile:
            raise StoreNotFound(f"There is no store with the id of {id}")

        db_products = await product_repo.get_products_from_store_by_id(
            store_id=id
        )

        completed_products = await attach_related_info_to_products(
            products=db_products,
            tag_repo=tag_repo,
            menu_category_repo=menu_category_repo
        )

        products_by_menu_categories = group_products_by_menu_category(
            completed_products
        )

        return {
            **db_store_profile.model_dump(),
            "products_by_menu_categories": products_by_menu_categories
        }
    except StoreNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    except Exception as exc:
        stores_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, 
            "Failed to fetch product."
        )

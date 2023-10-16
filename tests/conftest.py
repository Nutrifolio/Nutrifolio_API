import warnings
import os
import pytest
import pytest_asyncio
from typing import BinaryIO, Generator, AsyncGenerator
from fastapi import FastAPI
from databases import Database
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from app.api.main import get_application
from app.api.dependencies.space_bucket import get_sb_client

from app.db.repositories.users import UsersRepository
from app.db.repositories.stores import StoresRepository
from app.db.repositories.store_profiles import StoreProfilesRepository
from app.db.repositories.products import ProductsRepository
from app.db.repositories.product_details import ProductDetailsRepository
from app.db.repositories.product_tags import ProductTagsRepository
from app.db.repositories.product_menu_categories import ProductMenuCategoriesRepository

from app.models.users import UserCreate, UserInDB
from app.models.stores import StoreCreate, StoreInDB
from app.models.store_profiles import StoreProfileCreate, StoreProfileInDB

from app.services import auth_service
from app.core.config import SECRET_KEY

import alembic
from alembic.config import Config


# Apply migrations at beginning of the testing session and roll them back at the end
@pytest.fixture(scope="session")
def apply_migrations() -> Generator[None, None, None]:
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    os.environ["TESTING"] = "1"
    config = Config("alembic.ini")

    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


# Create a new FastAPI instance for testing
@pytest.fixture
def app(apply_migrations: None) -> FastAPI:
    return get_application()


# Truncate all tables in the test database between tests
@pytest_asyncio.fixture(autouse=True)
async def setup(app: FastAPI) -> AsyncGenerator[None, None]:
    async with LifespanManager(app):
        await app.state._conn_pool.execute("SELECT truncate_tables();")
    yield


# Grab a reference to our connection pool when needed
@pytest.fixture
def db(app: FastAPI) -> Database:
    return app.state._conn_pool


#################### Create repositories ####################
@pytest.fixture
def user_repo(db: Database) -> UsersRepository:
    return UsersRepository(db)

@pytest.fixture
def store_repo(db: Database) -> StoresRepository:
    return StoresRepository(db)

@pytest.fixture
def store_profile_repo(db: Database) -> StoreProfilesRepository:
    return StoreProfilesRepository(db)

@pytest.fixture
def product_repo(db: Database) -> ProductsRepository:
    return ProductsRepository(db)

@pytest.fixture
def product_details_repo(db: Database) -> ProductDetailsRepository:
    return ProductDetailsRepository(db)

@pytest.fixture
def product_tag_repo(db: Database) -> ProductTagsRepository:
    return ProductTagsRepository(db)

@pytest.fixture
def product_menu_category_repo(db: Database) -> ProductMenuCategoriesRepository:
    return ProductMenuCategoriesRepository(db)
############################################################


# Create an asynchronous HTTP client to make requests in our tests
@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test-server") as client:
            yield client


# Create a test user in the database
@pytest_asyncio.fixture
async def test_user(user_repo: UsersRepository) -> UserInDB:
    new_user = UserCreate(
        email="test_email@gmail.com",
        password="mysecretpassword",
        conf_password="mysecretpassword",
    )

    return await user_repo.register_new_user(new_user=new_user)


# Create an authorized client to test endpoints requiring user authentication
@pytest.fixture
def authorized_client_for_test_user(
    client: AsyncClient, test_user: UserInDB
) -> AsyncClient:
    access_token = auth_service.create_access_token_for_user(
        user_id=test_user.id,
        secret_key=str(SECRET_KEY)
    )
 
    client.headers = {
        **client.headers,
        "Authorization": f"bearer {access_token}",
    }
 
    return client


# Create a test store in the database
@pytest_asyncio.fixture
async def test_store(store_repo: StoresRepository) -> StoreInDB:
    new_store = StoreCreate(
        email="test_email@mystore.com",
        password="mysecretpassword",
        conf_password="mysecretpassword",
    )

    return await store_repo.register_new_store(new_store=new_store)


# Create a verified test store
@pytest_asyncio.fixture
async def verified_test_store(
    db: Database, store_repo: StoresRepository
) -> StoreInDB:
    new_store = StoreCreate(
        email="test_email@mystore.com",
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


# Create an authorized client to test endpoints requiring store authentication
@pytest.fixture
def authorized_client_for_verified_test_store(
    client: AsyncClient, verified_test_store: StoreInDB
) -> AsyncClient:
    access_token = auth_service.create_access_token_for_store(
        store_id=verified_test_store.id,
        secret_key=str(SECRET_KEY)
    )
 
    client.headers = {
        **client.headers,
        "Authorization": f"bearer {access_token}",
    }
 
    return client


@pytest.fixture
def mock_sb_client(app: FastAPI):
    def sb_client():
        class S3Client:
            def upload_fileobj(
                self, Fileobj: BinaryIO, Bucket: str, Key: str, ExtraArgs: dict
            ) -> bool:
                return True
        return S3Client()

    app.dependency_overrides[get_sb_client] = sb_client
    yield
    del app.dependency_overrides[get_sb_client]

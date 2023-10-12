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
from app.models.products import ProductCreate, ProductInDB
from app.db.repositories.products import ProductsRepository
from app.models.users import UserCreate, UserInDB
from app.db.repositories.users import UsersRepository
from app.models.stores import StoreCreate, StoreInDB
from app.db.repositories.stores import StoresRepository
from app.models.store_profiles import StoreProfileCreate, StoreProfileInDB
from app.db.repositories.store_profiles import StoreProfilesRepository
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


# Create an asynchronous HTTP client to make requests in our tests
@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test-server") as client:
            yield client


# Create a test user in the database
@pytest_asyncio.fixture
async def test_user(db: Database) -> UserInDB:
    new_user = UserCreate(
        email="test_email@gmail.com",
        password="mysecretpassword",
        conf_password="mysecretpassword",
    )
 
    user_repo = UsersRepository(db)
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
async def test_store(db: Database) -> StoreInDB:
    new_store = StoreCreate(
        email="test_email@mystore.com",
        password="mysecretpassword",
        conf_password="mysecretpassword",
    )
 
    store_repo = StoresRepository(db)
    return await store_repo.register_new_store(new_store=new_store)


# Create the profile of the test store in the database
@pytest_asyncio.fixture
async def test_store_profile(db: Database, test_store: StoreInDB) -> StoreInDB:
    new_store_profile = StoreProfileCreate(
        name="test_store",
        description="test_desc",
        phone_number=6943444546,
        address="test_address",
        lat=38.214,
        lng=23.812,
        store_id=test_store.id
    )

    store_profile_repo = StoreProfilesRepository(db)
    return await store_profile_repo.create_new_store_profile(
        new_store_profile=new_store_profile
    )


# Create a verified test store
@pytest_asyncio.fixture
async def verified_test_store(db: Database) -> StoreInDB:
    new_store = StoreCreate(
        email="test_email@mystore.com",
        password="mysecretpassword",
        conf_password="mysecretpassword",
    )

    store_repo = StoresRepository(db)
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


# Create the profile of the test store in the database
@pytest_asyncio.fixture
async def verified_test_store_profile(
    db: Database, verified_test_store: StoreInDB
) -> StoreInDB:
    new_store_profile = StoreProfileCreate(
        name="test_store",
        description="test_desc",
        phone_number=6943444546,
        address="test_address",
        lat=38.214,
        lng=23.812,
        store_id=verified_test_store.id
    )

    store_profile_repo = StoreProfilesRepository(db)
    return await store_profile_repo.create_new_store_profile(
        new_store_profile=new_store_profile
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


@pytest_asyncio.fixture
async def test_product(
    db: Database, verified_test_store: StoreInDB
) -> ProductInDB:
    new_product = ProductCreate(
        name="test product",
        description="test description 1",
        price=1.00,
        has_details=False,
        is_public=True,
        store_id=verified_test_store.id
    )

    product_repo = ProductsRepository(db)
    return await product_repo.create_product(new_product=new_product)


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

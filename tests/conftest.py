import warnings
import os
import pytest
import pytest_asyncio
from typing import Generator, AsyncGenerator
from fastapi import FastAPI
from databases import Database
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from app.api.main import get_application
from app.models.products import ProductCreate, ProductInDB
from app.db.repositories.products import ProductsRepository
from app.models.users import UserCreate, UserInDB
from app.db.repositories.users import UsersRepository
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
        async with AsyncClient(
            app=app,
            base_url="http://test-server",
            headers={"Content-Type": "application/json"}
        ) as client:
            yield client


# Create a test product in the database
@pytest_asyncio.fixture
async def test_product(db: Database) -> ProductInDB:
    new_product = ProductCreate(
        name="test product",
        description="test description",
        price=1.00,
    )

    product_repo = ProductsRepository(db)
    return await product_repo.create_product(new_product=new_product)


# Create a test user in the database
@pytest_asyncio.fixture
async def test_user(db: Database) -> UserInDB:
    new_user = UserCreate(
        username="test_username",
        email="test_email@gmail.com",
        password="mysecretpassword",
        conf_password="mysecretpassword",
    )
 
    user_repo = UsersRepository(db)
    return await user_repo.register_new_user(new_user=new_user)


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

from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret


config = Config()

PROJECT_NAME = "Nutrifolio-API"
VERSION = "0.1.0"

DSN = config("DSN", cast=str)

SECRET_KEY = config("SECRET_KEY", cast=Secret)
JWT_ALGORITHM = config("JWT_ALGORITHM", cast=str, default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    cast=int,
    default=7 * 24 * 60  # one week
)

DATABASE_HOST = config("DATABASE_HOST", cast=str, default="postgis-db")
DATABASE_PORT = config("DATABASE_PORT", cast=str, default="5432")
DATABASE_NAME = config("DATABASE_NAME", cast=str)
DATABASE_USER = config("DATABASE_USER", cast=str)
DATABASE_PASSWORD = config("DATABASE_PASSWORD", cast=Secret)
MIN_CONNECTION_COUNT = config("MIN_CONNECTION_COUNT", cast=int, default=0)
MAX_CONNECTION_COUNT = config("MAX_CONNECTION_COUNT", cast=int, default=100)

DATABASE_URL = config(
  "DATABASE_URL",
  cast=DatabaseURL,
  default=f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)

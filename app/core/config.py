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

DO_ACCESS_KEY = config("DO_ACCESS_KEY", cast=str)
DO_SECRET_KEY = config("DO_SECRET_KEY", cast=Secret)
DO_SPACE_BUCKET_URL = config("DO_SPACE_BUCKET_URL", cast=str)

REDIS_HOST = config("REDIS_HOST", cast=str, default="redis-cache")
REDIS_PORT = config("REDIS_PORT", cast=str, default="6379")
REDIS_DB = config("REDIS_DB", cast=int, default=0)

REDIS_URL = config(
    "REDIS_URL",
    cast=str,
    default=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
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

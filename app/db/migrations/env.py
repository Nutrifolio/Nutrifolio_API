import os
import alembic
from sqlalchemy import engine_from_config, create_engine, pool
from psycopg2 import DatabaseError

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))
from app.core.config import DATABASE_URL, DATABASE_NAME
DATABASE_URL = str(DATABASE_URL)

import logging
from logging.config import fileConfig


# Alembic Config object, which provides access to values within the .ini file
config = alembic.context.config

# Interpret the config file for logging
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode
    """
    DB_URL = f"{DATABASE_URL}_test" if os.environ.get("TESTING") else DATABASE_URL

    if os.environ.get("TESTING"):
        default_engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
        with default_engine.connect() as default_conn:
            default_conn.execute(f"DROP DATABASE IF EXISTS {DATABASE_NAME}_test")
            default_conn.execute(f"CREATE DATABASE {DATABASE_NAME}_test")
        
        test_engine = create_engine(DB_URL, isolation_level="AUTOCOMMIT")
        with test_engine.connect() as test_conn:
            test_conn.execute("CREATE EXTENSION postgis;")

    connectable = config.attributes.get("connection", None)
    config.set_main_option("sqlalchemy.url", DB_URL)

    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        alembic.context.configure(
            connection=connection,
            target_metadata=None
        )

        with alembic.context.begin_transaction():
            alembic.context.run_migrations()


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    """
    if os.environ.get("TESTING"):
        raise DatabaseError("Running testing migrations offline currently not supported.")

    alembic.context.configure(url=DATABASE_URL)
 
    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


if alembic.context.is_offline_mode():
    logger.info("Running migrations offline")
    run_migrations_offline()
else:
    logger.info("Running migrations online")
    run_migrations_online()

import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import pool
from alembic import context

from src.db.models import Base
from src.core.settings import settings

# Config object from alembic.ini
config = context.config

# Setup logging from config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models
target_metadata = Base.metadata

# DB URL
DATABASE_URL = f"sqlite+aiosqlite:///{settings.app.db_path}"  # добавим в .env позже

config.set_main_option("sqlalchemy.url", DATABASE_URL)

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode."""

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:

        def do_migrations(connection):
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
            context.run_migrations()

        await connection.run_sync(do_migrations)


def run():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())

run()

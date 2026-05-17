"""
Alembic env.py — Cấu hình migration environment.
Hỗ trợ cả online mode (apply migration) và offline mode (generate SQL script).
Load DATABASE_URL từ app/core/config.py — KHÔNG hardcode credentials.
"""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# ──────────────────────────────────────────────
# Import tất cả models để Alembic nhận diện metadata
# QUAN TRỌNG: Phải import __init__.py của models để autogenerate hoạt động đúng
# ──────────────────────────────────────────────
from app.core.config import settings
from app.core.database import Base
import app.domain.models  # noqa: F401 — trigger import tất cả models

# Alembic Config object
config = context.config

# Đọc logging config từ alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata từ Base
target_metadata = Base.metadata

# Override sqlalchemy.url bằng SYNC URL (dùng cho offline mode)
config.set_main_option("sqlalchemy.url", settings.SYNC_DATABASE_URL)


# ──────────────────────────────────────────────
# Offline migration (generate SQL script)
# ──────────────────────────────────────────────
def run_migrations_offline() -> None:
    """Chạy migration ở offline mode — sinh SQL script thay vì kết nối DB."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ──────────────────────────────────────────────
# Online migration (apply to database)
# ──────────────────────────────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Chạy migration với async engine.
    Dùng DATABASE_URL (asyncpg) trực tiếp thay vì lấy từ ini config.
    """
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point cho online migration."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


"""
pytest conftest.py — Test fixtures và configuration cơ bản.
Dùng cho toàn bộ backend test suite.

Test isolation strategy:
  - Schema tạo 1 lần/session (scope="session") — nhanh hơn nhiều
  - Mỗi test chạy trong SAVEPOINT (nested transaction) → tự rollback sau khi test xong
  - Không ảnh hưởng dữ liệu giữa các tests

Fix asyncpg event loop issue:
  - Dùng NullPool để tắt connection pooling — tránh "Future attached to a different loop"
  - Engine tạo bên trong session fixture thay vì module level
"""
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.database import Base
# BẮT BUỘC: Import tất cả models để Base.metadata biết toàn bộ bảng khi create_all chạy.
# Nếu thiếu, Base.metadata.create_all() sẽ bỏ sót bảng → test fail với "relation does not exist".
import app.domain.models  # noqa: F401

# Alias để tránh conflict với `app` package
from main import app as fastapi_app


# ──────────────────────────────────────────────
# Test Database URL — parse an toàn, không dùng string.replace() thô
# ──────────────────────────────────────────────
def _build_test_db_url(base_url: str) -> str:
    """
    Thay đổi tên database sang '_test' một cách an toàn.
    VD: postgresql+asyncpg://user:pass@host:5432/qschool → /qschool_test
    Tránh bug nếu DB name chứa 'qschool' ở các vị trí khác.
    """
    if "/" not in base_url.split("@")[-1]:
        raise ValueError(f"Không parse được DB name từ URL: {base_url}")
    host_part, _, db_name = base_url.rpartition("/")
    if db_name.endswith("_test"):
        return base_url
    return f"{host_part}/{db_name}_test"


TEST_DATABASE_URL = _build_test_db_url(settings.DATABASE_URL)


# ──────────────────────────────────────────────
# Engine — tạo bên trong fixture để bind đúng event loop
# NullPool: tắt connection pool → mỗi connection tạo mới, tránh "Future attached to a different loop"
# ──────────────────────────────────────────────
@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Tạo engine 1 lần/session với NullPool để tránh asyncpg loop conflict."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,  # Tắt pooling — critical cho pytest-asyncio
    )

    # Tạo toàn bộ schema 1 lần khi bắt đầu test session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Teardown: drop schema sau khi toàn bộ test session kết thúc
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# ──────────────────────────────────────────────
# DB Session — SAVEPOINT-based transaction isolation
# Mỗi test chạy trong nested transaction, tự rollback sau khi xong
# ──────────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Transaction isolation per test — SQLAlchemy 2.x compatible.

    Dùng connection-level SAVEPOINT thay vì session-level begin() để tránh
    "Can't reconnect until invalid transaction is rolled back" error trên SA 2.x.
    """
    async with test_engine.connect() as conn:
        await conn.begin()                             # Outer transaction
        nested = await conn.begin_nested()             # SAVEPOINT

        async with AsyncSession(bind=conn, expire_on_commit=False) as session:
            try:
                yield session
            finally:
                if nested.is_active:
                    await nested.rollback()

        await conn.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client với DB session override."""
    async def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://testserver",
    ) as c:
        yield c

    fastapi_app.dependency_overrides.clear()

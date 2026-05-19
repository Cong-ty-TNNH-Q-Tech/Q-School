"""
pytest conftest.py — Test fixtures và configuration cơ bản.
Dùng cho toàn bộ backend test suite.

Test isolation strategy:
  - Schema tạo 1 lần/session (scope="session")
  - Mỗi test chạy trong SAVEPOINT (nested transaction) → tự rollback sau khi test xong

Fix asyncpg event loop issue:
  - Patch `app.core.database.engine` thành NullPool engine tại import time
    → lifespan + get_db đều dùng NullPool engine → không còn loop conflict
  - NullPool: mỗi lần connect tạo connection mới, không cache cross-loop
"""
from typing import AsyncGenerator
from unittest.mock import patch

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base

# BẮT BUỘC: Import tất cả models để Base.metadata biết toàn bộ bảng khi create_all chạy.
import app.domain.models  # noqa: F401


# ──────────────────────────────────────────────
# Test Database URL
# ──────────────────────────────────────────────
def _build_test_db_url(base_url: str) -> str:
    if "/" not in base_url.split("@")[-1]:
        raise ValueError(f"Không parse được DB name từ URL: {base_url}")
    host_part, _, db_name = base_url.rpartition("/")
    if db_name.endswith("_test"):
        return base_url
    return f"{host_part}/{db_name}_test"


TEST_DATABASE_URL = _build_test_db_url(settings.DATABASE_URL)

# ──────────────────────────────────────────────
# Tạo NullPool engine dùng xuyên suốt test session
# Phải tạo ở module level TRƯỚC khi app được import
# để patch có thể replace đúng object
# ──────────────────────────────────────────────
_test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)
_test_session_factory = async_sessionmaker(
    bind=_test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ──────────────────────────────────────────────
# Patch production engine trước khi import app
# ──────────────────────────────────────────────
import app.core.database as _db_module  # noqa: E402

_db_module.engine = _test_engine
_db_module.AsyncSessionFactory = _test_session_factory

# Import app SAU KHI patch engine
from main import app as fastapi_app  # noqa: E402
from app.core.dependencies import get_db  # noqa: E402


# ──────────────────────────────────────────────
# Schema — tạo 1 lần/session
# ──────────────────────────────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_schema():
    """Tạo toàn bộ schema 1 lần khi bắt đầu test session."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _test_engine.dispose()


# ──────────────────────────────────────────────
# DB Session — SAVEPOINT-based transaction isolation
# ──────────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Transaction isolation per test — rollback sau mỗi test."""
    async with _test_engine.connect() as conn:
        await conn.begin()
        nested = await conn.begin_nested()

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

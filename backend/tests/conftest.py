"""
pytest conftest.py — Test fixtures và configuration cơ bản.
Dùng cho toàn bộ backend test suite.

Test isolation strategy:
  - Engine + schema tạo 1 lần/session (nhanh, ít overhead)
  - Mỗi test dùng connection riêng biệt để tránh asyncpg loop conflict
  - Không rollback giữa tests — thay vào đó mỗi test hoạt động độc lập
    (test register đăng ký user mới, test login dùng user mới...)

Fix asyncpg event loop:
  - Dùng NullPool — không cache connection → không bị "Future attached to different loop"
  - Engine tạo bên trong session fixture để bind đúng event loop
  - Không dùng module-level engine (gây loop conflict)
"""
from typing import AsyncGenerator
from contextlib import asynccontextmanager

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base
from app.core.dependencies import get_db

# BẮT BUỘC: Import tất cả models để Base.metadata biết toàn bộ bảng khi create_all chạy.
import app.domain.models  # noqa: F401

# Import FastAPI app — dùng alias để tránh conflict với `app` package
from main import app as _fastapi_app


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
# Session-scoped fixtures: schema setup/teardown
# Engine tạo bên trong fixture → bind đúng event loop của pytest-asyncio
# ──────────────────────────────────────────────
@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """
    Engine với NullPool — tạo bên trong session fixture.
    NullPool: không pool connection → tránh asyncpg loop conflict hoàn toàn.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ──────────────────────────────────────────────
# Function-scoped DB session
# ──────────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Mỗi test nhận 1 AsyncSession độc lập.
    NullPool đảm bảo connection mới được tạo trong event loop hiện tại.
    Dùng BEGIN + SAVEPOINT để rollback sau test.
    """
    async with test_engine.connect() as conn:
        trans = await conn.begin()
        nested = await conn.begin_nested()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            if nested.is_active:
                await nested.rollback()
            await trans.rollback()


# ──────────────────────────────────────────────
# HTTP test client
# ──────────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    ASGI test client với:
    - DB session override (dùng test DB thay vì production DB)
    - lifespan bypass: tạo lifespan noop để tránh production engine startup
    """

    @asynccontextmanager
    async def noop_lifespan(app: FastAPI):
        """Thay thế lifespan production để bỏ qua DB/Redis health check."""
        yield

    async def override_get_db():
        yield db_session

    # Tạm thời replace lifespan để skip production startup
    original_lifespan = _fastapi_app.router.lifespan_context
    _fastapi_app.router.lifespan_context = noop_lifespan

    _fastapi_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=_fastapi_app),
        base_url="http://testserver",
    ) as c:
        yield c

    # Restore
    _fastapi_app.dependency_overrides.clear()
    _fastapi_app.router.lifespan_context = original_lifespan

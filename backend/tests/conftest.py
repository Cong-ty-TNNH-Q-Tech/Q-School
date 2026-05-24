"""
pytest conftest.py — Test fixtures và configuration cơ bản.
Dùng cho toàn bộ backend test suite.

Test isolation strategy:
  - Dùng function-scope cho tất cả async fixtures (mỗi test có event loop riêng)
  - NullPool engine: không pool connection, tạo fresh connection mỗi lần
  - Mỗi test nhận client + db_session riêng

Fix asyncpg "Future attached to a different loop":
  - asyncio_mode=auto + function scope → mỗi test có event loop riêng
  - Engine + session tạo trong function scope → bind đúng event loop của test đó
  - Bypass production lifespan (DB/Redis health check) bằng noop_lifespan
    để tránh production pool tạo connection ở loop sai
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

# Import FastAPI app — alias để tránh conflict với `app` package trong sys.path
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
# Schema setup — chạy 1 lần trước tất cả tests (sync, không async)
# Dùng synchronous psycopg2 để tránh vấn đề event loop
# ──────────────────────────────────────────────
import pytest
import asyncio


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def setup_schema():
    """Tạo schema 1 lần/session, drop khi xong. Dùng engine riêng."""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

    yield

    engine2 = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)
    async with engine2.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine2.dispose()


# ──────────────────────────────────────────────
# Function-scoped engine + session
# Mỗi test có engine + session riêng bind vào event loop của test đó
# ──────────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def db_session(setup_schema) -> AsyncGenerator[AsyncSession, None]:
    """
    Mỗi test nhận AsyncSession riêng, engine NullPool.
    - setup_schema đảm bảo schema đã tạo trước khi test chạy
    - NullPool: connection mới hoàn toàn, bind đúng event loop hiện tại
    """
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)

    async with engine.connect() as conn:
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

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    ASGI test client:
    - Override get_db với test session
    - Bypass production lifespan (noop) để tránh production engine startup
    """

    @asynccontextmanager
    async def noop_lifespan(app: FastAPI):
        yield

    async def override_get_db():
        yield db_session

    original_lifespan = _fastapi_app.router.lifespan_context
    _fastapi_app.router.lifespan_context = noop_lifespan
    _fastapi_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=_fastapi_app),
        base_url="http://testserver",
    ) as c:
        yield c

    _fastapi_app.dependency_overrides.clear()
    _fastapi_app.router.lifespan_context = original_lifespan

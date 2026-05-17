"""
pytest conftest.py — Test fixtures và configuration cơ bản.
Dùng cho toàn bộ backend test suite.

Test isolation strategy:
  - Schema tạo 1 lần/session (scope="session") — nhanh hơn nhiều
  - Mỗi test chạy trong SAVEPOINT (nested transaction) → tự rollback sau khi test xong
  - Không ảnh hưởng dữ liệu giữa các tests
"""
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.core.database import Base
from app.core.dependencies import get_db
from main import app

# ──────────────────────────────────────────────
# Test Database URL — parse an toàn, không dùng string.replace() thô
# ──────────────────────────────────────────────
def _build_test_db_url(base_url: str) -> str:
    """
    Thay đổi tên database sang '_test' một cách an toàn.
    VD: postgresql+asyncpg://user:pass@host:5432/qschool → /qschool_test
    Tránh bug nếu DB name chứa 'qschool' ở các vị trí khác.
    """
    # Tách phần path (sau dấu / cuối cùng) và thay thế
    if "/" not in base_url.split("@")[-1]:
        raise ValueError(f"Không parse được DB name từ URL: {base_url}")
    # Lấy path cuối cùng sau @host:port
    host_part, _, db_name = base_url.rpartition("/")
    # Nếu db_name đã có _test thì dùng nguyên
    if db_name.endswith("_test"):
        return base_url
    return f"{host_part}/{db_name}_test"


TEST_DATABASE_URL = _build_test_db_url(settings.DATABASE_URL)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(
    bind=test_engine, class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ──────────────────────────────────────────────
# Schema — tạo 1 lần per test session (nhanh hơn per-test)
# ──────────────────────────────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_schema():
    """Tạo toàn bộ schema 1 lần khi bắt đầu test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Teardown: drop schema sau khi toàn bộ test session kết thúc
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


# pytest-asyncio >= 0.21: dùng asyncio_mode="auto" trong pytest.ini
@pytest.fixture(scope="session")
def event_loop_policy():
    """Dùng asyncio default policy."""
    return asyncio.DefaultEventLoopPolicy()


# ──────────────────────────────────────────────
# DB Session — SAVEPOINT-based transaction isolation
# Mỗi test chạy trong nested transaction, tự rollback sau khi xong
# ──────────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Transaction isolation per test.
    Dùng SAVEPOINT (nested transaction) để đảm bảo mỗi test clean slate.
    """
    async with TestSessionFactory() as session:
        # Bắt đầu outer transaction
        async with session.begin():
            # Tạo SAVEPOINT để nested rollback không ảnh hưởng outer
            nested = await session.begin_nested()
            try:
                yield session
            finally:
                # Rollback SAVEPOINT — dữ liệu test không persist
                await nested.rollback()
        # Outer transaction KHÔNG commit — DB clean sau mỗi test


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client với DB session override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as c:
        yield c

    app.dependency_overrides.clear()

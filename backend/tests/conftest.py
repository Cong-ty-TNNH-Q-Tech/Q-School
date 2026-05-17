"""
pytest conftest.py — Test fixtures và configuration cơ bản.
Dùng cho toàn bộ backend test suite.
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
# Test Database — dùng DB riêng để không ảnh hưởng production
# ──────────────────────────────────────────────
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/qschool", "/qschool_test")

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionFactory = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


# pytest-asyncio >= 0.21: dùng asyncio_mode="auto" trong pytest.ini hoặc mọi fixture phải có @pytest_asyncio.fixture
# event_loop fixture scope="session" bị deprecated từ pytest-asyncio 0.21 — dùng loop_scope thay
@pytest.fixture(scope="session")
def event_loop_policy():
    """Dùng asyncio default policy."""
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Mỗi test nhận một transaction riêng, tự động rollback sau khi test xong."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionFactory() as session:
        try:
            yield session
        finally:
            await session.rollback()


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

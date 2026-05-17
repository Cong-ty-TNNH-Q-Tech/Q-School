"""
Database — Async SQLAlchemy engine, session factory, và Base declarative model.
Sử dụng asyncpg driver để đạt hiệu năng tối đa với async/await.
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# ──────────────────────────────────────────────
# Engine
# ──────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,          # Log SQL queries khi DEBUG=True
    pool_pre_ping=True,           # Kiểm tra connection trước khi sử dụng
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800,            # Recycle connections sau 30 phút (tránh stale qua load balancer)
)

# ──────────────────────────────────────────────
# Session factory
# ──────────────────────────────────────────────
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,       # Tránh lazy-load sau commit trong async context
    autocommit=False,
    autoflush=False,
)


# ──────────────────────────────────────────────
# Declarative Base — Tất cả ORM models kế thừa từ đây
# ──────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ──────────────────────────────────────────────
# Utility: Tạo / xóa tất cả bảng (chỉ dùng trong testing)
# ──────────────────────────────────────────────
async def create_all_tables() -> None:
    """Tạo tất cả bảng. Chỉ dùng cho development/test — Production dùng Alembic."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables() -> None:
    """Xóa tất cả bảng. NGUY HIỂM — Chỉ dùng trong test teardown."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

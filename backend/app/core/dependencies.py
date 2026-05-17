"""
FastAPI Dependencies — get_db, get_current_user, get_current_teacher, etc.
Dùng với Depends() trong các Router để inject dependencies.
"""
from typing import AsyncGenerator, Annotated, TYPE_CHECKING
import uuid

from fastapi import Depends, Header
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionFactory
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException

if TYPE_CHECKING:
    from app.domain.models.user import User


# ──────────────────────────────────────────────
# Database Session
# ──────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield một AsyncSession cho mỗi request.
    Đảm bảo session được đóng sau khi request hoàn thành.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


DbDep = Annotated[AsyncSession, Depends(get_db)]


# ──────────────────────────────────────────────
# Current User (từ JWT Bearer Token)
# ──────────────────────────────────────────────
async def get_current_user(
    db: DbDep,
    authorization: Annotated[str | None, Header()] = None,
) -> "User":
    """
    Xác thực JWT Bearer Token từ Authorization header.
    Trả về User ORM object (không phải dict).
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1]

    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedException("Invalid or expired token")

    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type")

    user_id = payload.get("sub")
    role = payload.get("role")

    if not user_id:
        raise UnauthorizedException("Token payload is malformed")

    # Lazy import để tránh circular dependency
    from app.domain.models.user import User

    result = await db.execute(
        select(User).where(
            User.id == uuid.UUID(user_id),
            User.deleted_at.is_(None),
            User.is_active.is_(True),
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("User not found or deactivated")

    return user


CurrentUserDep = Annotated["User", Depends(get_current_user)]


# ──────────────────────────────────────────────
# Role-based Guards
# ──────────────────────────────────────────────
async def require_teacher(current_user: CurrentUserDep):
    """Chỉ cho phép role 'teacher' hoặc 'admin' truy cập."""
    if current_user.role not in ("teacher", "admin"):
        raise ForbiddenException("Teacher role required")
    return current_user


async def require_admin(current_user: CurrentUserDep):
    """Chỉ cho phép role 'admin' truy cập."""
    if current_user.role != "admin":
        raise ForbiddenException("Admin role required")
    return current_user


TeacherDep = Annotated["User", Depends(require_teacher)]
AdminDep = Annotated["User", Depends(require_admin)]

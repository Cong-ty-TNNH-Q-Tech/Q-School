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

    # Validate UUID format trước khi query DB
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise UnauthorizedException("Token payload contains invalid user ID")

    result = await db.execute(
        select(User).where(
            User.id == user_uuid,
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


# ──────────────────────────────────────────────
# SaaS Billing Guard (AGENTS.md requirement)
# Sử dụng cho TấT CẢ AI API routes
# ──────────────────────────────────────────────
async def require_active_subscription(current_user: CurrentUserDep, db: DbDep) -> "User":
    """
    Kiểm tra user có subscription đang active hay không.
    Dùng làm dependency cho mọi AI route (Chat, Generate, RAG).

    Raise PaymentRequiredException (402) nếu:
      - Không có subscription nào
      - Subscription đã hết hạn (current_period_end < now)
      - Subscription bị cancel

    TODO (khi billing implement):
      1. Query UserSubscription theo user_id + status='active'
      2. Kiểm tra current_period_end > datetime.now(timezone.utc)
      3. Kiểm tra daily AI usage quota từ Redis
    """
    from datetime import datetime, timezone
    from sqlalchemy import and_
    from app.core.exceptions import PaymentRequiredException
    from app.domain.models.billing import UserSubscription

    result = await db.execute(
        select(UserSubscription).where(
            and_(
                UserSubscription.user_id == current_user.id,
                UserSubscription.status == "active",
                UserSubscription.current_period_end > datetime.now(timezone.utc),
            )
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise PaymentRequiredException(
            "No active subscription. Please upgrade your plan to use AI features."
        )

    return current_user


AIUserDep = Annotated["User", Depends(require_active_subscription)]
"""Dùng dependency này thay vì CurrentUserDep cho tất cả AI endpoints."""

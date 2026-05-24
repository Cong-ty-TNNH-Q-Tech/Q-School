"""
UserSQLAlchemyRepository — Concrete implementation của IUserRepository.
Đây là PATTERN MẪU cho các Repository khác.

Cấu trúc implement:
  1. Kế thừa BaseRepository[User] để có CRUD cơ bản miễn phí
  2. Implement tất cả abstract methods từ IUserRepository (Port)
  3. Thêm các query đặc thù của User ngoài CRUD cơ bản

Member: Copy pattern này khi tạo ClassRepository, QuizRepository...
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.user_repository import IUserRepository
from app.domain.models.user import User, Profile


class UserSQLAlchemyRepository(BaseRepository[User], IUserRepository):
    """
    Concrete Repository: Truy cập DB cho User bằng SQLAlchemy Async.
    Kế thừa BaseRepository để tái dụng get_by_id, create, update, soft_delete.
    Implement IUserRepository để Use Cases có thể inject qua interface.

    Inject vào Use Case qua FastAPI Depends — xem app/core/dependencies.py.
    """

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    # ──────────────────────────────────────────────
    # Interface methods (IUserRepository)
    # ──────────────────────────────────────────────
    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Lấy User theo ID, eager load Profile để tránh N+1."""
        stmt = (
            select(User)
            .options(selectinload(User.profile))
            .where(
                User.id == user_id,
                User.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Lấy User theo email (case-insensitive). Dùng cho login."""
        stmt = (
            select(User)
            .options(selectinload(User.profile))
            .where(
                User.email == email.lower().strip(),
                User.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Lấy User theo username. Dùng cho login."""
        stmt = (
            select(User)
            .options(selectinload(User.profile))
            .where(
                User.username == username.strip(),
                User.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str = "student",
    ) -> User:
        """
        Tạo User mới + Profile rỗng đi kèm (1:1 relationship).
        Profile được tạo cùng lúc để đảm bảo data consistency.
        """
        user = User(
            username=username.strip(),
            email=email.lower().strip(),
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        self.db.add(user)
        await self.db.flush()  # Lấy user.id mà không commit

        # Tạo Profile rỗng đi kèm
        profile = Profile(user_id=user.id)
        self.db.add(profile)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def update(self, user: User, **kwargs) -> User:
        """Delegate lên BaseRepository.update()."""
        return await super().update(user, **kwargs)

    async def soft_delete(self, user: User) -> User:
        """Delegate lên BaseRepository.soft_delete()."""
        return await super().soft_delete(user)

    # ──────────────────────────────────────────────
    # Extra queries (ngoài IUserRepository interface)
    # ──────────────────────────────────────────────
    async def is_email_taken(self, email: str) -> bool:
        """Kiểm tra email đã được đăng ký (kể cả soft-deleted) để tránh duplicate."""
        stmt = select(User.id).where(User.email == email.lower().strip())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def is_username_taken(self, username: str) -> bool:
        """Kiểm tra username đã tồn tại (kể cả soft-deleted)."""
        stmt = select(User.id).where(User.username == username.strip())
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

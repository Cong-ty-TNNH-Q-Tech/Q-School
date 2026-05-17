"""
Base Repository — Generic CRUD pattern với SQLAlchemy Async.
Áp dụng Repository Pattern để tách biệt logic nghiệp vụ khỏi ORM.
"""
from typing import Generic, TypeVar, Type, Any, Sequence
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic Repository cung cấp CRUD cơ bản cho tất cả models.
    Use Cases kế thừa hoặc sử dụng repo này thay vì query SQLAlchemy trực tiếp.

    Ví dụ sử dụng:
        user_repo = BaseRepository(User, db)
        user = await user_repo.get_by_id(user_id)
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        self.model = model
        self.db = db

    async def get_by_id(self, id: uuid.UUID) -> ModelType | None:
        """Lấy record theo ID. Tự động lọc soft-deleted nếu model có deleted_at."""
        stmt = select(self.model).where(self.model.id == id)

        # Lọc Soft Delete nếu model hỗ trợ
        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        filters: list[Any] | None = None,
    ) -> Sequence[ModelType]:
        """
        Offset pagination — CHỈ dùng cho bảng nhỏ/static (VD: Plans, Roles).
        TUYỆT ĐỐI KHÔNG dùng cho streaming data (Chat, Feed) — dùng cursor_paginate().
        """
        stmt = select(self.model)

        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))

        if filters:
            stmt = stmt.where(*filters)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def cursor_paginate(
        self,
        *,
        cursor: uuid.UUID | None = None,
        limit: int = 20,
        filters: list[Any] | None = None,
    ) -> Sequence[ModelType]:
        """
        Cursor Pagination — Bắt buộc dùng cho streaming data (ChatMessage, Feed).
        cursor: ID của phần tử cuối cùng đã fetch (None = từ đầu).

        AGENTS.md: TUYỆT ĐỐI không dùng offset pagination cho bảng liên tục thay đổi.
        """
        stmt = select(self.model)

        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))

        if cursor is not None:
            # Lấy records có id < cursor (giả định UUID v4 tăng dần theo created_at)
            stmt = stmt.where(self.model.id < cursor)

        if filters:
            stmt = stmt.where(*filters)

        # Order by id DESC để lấy records mới nhất trước
        stmt = stmt.order_by(self.model.id.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        """Tạo và lưu một record mới."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()  # Flush để lấy ID mà không commit
        await self.db.refresh(instance)
        return instance

    async def update(self, instance: ModelType, **kwargs) -> ModelType:
        """
        Cập nhật các fields của một record.
        Chỉ cho phép set các column hợp lệ — từ chối keys không tồn tại trong model.
        """
        valid_columns = {c.key for c in self.model.__table__.columns}
        invalid_keys = set(kwargs.keys()) - valid_columns
        if invalid_keys:
            raise ValueError(
                f"Invalid fields for {self.model.__name__}: {invalid_keys}. "
                f"Valid fields: {valid_columns}"
            )
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def soft_delete(self, instance: ModelType) -> ModelType:
        """
        Soft Delete — Đặt deleted_at = now().
        KHÔNG dùng db.delete() cho dữ liệu người dùng.
        """
        if not hasattr(instance, "deleted_at"):
            raise AttributeError(
                f"Model {self.model.__name__} không hỗ trợ Soft Delete. "
                "Thêm SoftDeleteMixin vào model."
            )
        instance.soft_delete()
        await self.db.flush()
        return instance

    async def count(self, filters: list[Any] | None = None) -> int:
        """Đếm số records (có lọc soft-deleted và filters tùy chọn)."""
        stmt = select(func.count()).select_from(self.model)

        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))

        if filters:
            stmt = stmt.where(*filters)

        result = await self.db.execute(stmt)
        return result.scalar_one()

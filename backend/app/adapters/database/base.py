"""
Base Repository — Generic CRUD pattern với SQLAlchemy Async.
Áp dụng Repository Pattern để tách biệt logic nghiệp vụ khỏi ORM.

CURSOR PAGINATION NOTE:
  UUID v4 là random — KHÔNG thể dùng 'id < cursor' để paginate theo thứ tự thời gian.
  Cursor PHẢI dựa vào created_at (timestamp monotonically tăng).
  API trả về cursor là ISO datetime string của record cuối cùng trong page.

ORM UPDATE NOTE (C1):
  SQLAlchemy onupdate=func.now() chỉ hoạt động với Core UPDATE expressions.
  Với ORM-style (setattr + flush), updated_at KHÔNG tự cập nhật.
  Fix: BaseRepository.update() luôn set updated_at=now() tường minh.
"""
from datetime import datetime, timezone
from typing import Generic, TypeVar, Type, Any, Sequence
import uuid

from sqlalchemy import select, func, or_, and_
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

    async def exists(self, id: uuid.UUID) -> bool:
        """
        Kiểm tra record có tồn tại và chưa bị soft-deleted hay không.
        SELECT chỉ id — không load full row để tránh lãng phí I/O.
        """
        stmt = select(self.model.id).where(self.model.id == id)
        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

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
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = 20,
        filters: list[Any] | None = None,
        ascending: bool = False,
    ) -> Sequence[ModelType]:
        """
        Cursor Pagination dựa trên (created_at, id) — COMPOSITE CURSOR.

        WHY NOT UUID ALONE:
          UUID v4 là random (không tăng dần theo thời gian).
          'id < cursor' với UUID v4 cho kết quả ngẫu nhiên, sai hoàn toàn.

        WHY COMPOSITE (created_at, id):
          Nếu nhiều records có cùng created_at (VD: bulk insert),
          chỉ dùng created_at làm cursor sẽ bỏ sót hoặc trùng records ở biên trang.
          Composite cursor (created_at, id) đảm bảo unique và stable pagination.

        HOW IT WORKS:
          - cursor_created_at + cursor_id: của record cuối cùng đã fetch (None = từ đầu)
          - ascending=False (default): lấy records MỚI hơn trước (inbox/chat)
          - ascending=True: lấy records CŨ hơn trước (scroll up lịch sử chat)

        API nên trả về cursor cho client:
          {
            "data": [...],
            "next_cursor_created_at": records[-1].created_at.isoformat() if has_more else None,
            "next_cursor_id": str(records[-1].id) if has_more else None
          }

        AGENTS.md: TUYỆT ĐỐI không dùng offset pagination cho bảng liên tục thay đổi.
        """
        if not hasattr(self.model, "created_at"):
            raise AttributeError(
                f"Model {self.model.__name__} không có 'created_at' — "
                "cursor_paginate() yêu cầu TimestampMixin."
            )

        stmt = select(self.model)

        if hasattr(self.model, "deleted_at"):
            stmt = stmt.where(self.model.deleted_at.is_(None))

        if cursor_created_at is not None:
            if ascending:
                # ascending=True (lịch sử chat — scroll up): lấy messages CŨ HƠN cursor
                # (created_at < cursor) OR (created_at == cursor AND id < cursor_id) — tiebreak bằng id
                if cursor_id is not None:
                    stmt = stmt.where(
                        or_(
                            self.model.created_at < cursor_created_at,
                            and_(
                                self.model.created_at == cursor_created_at,
                                self.model.id < cursor_id,
                            ),
                        )
                    )
                else:
                    stmt = stmt.where(self.model.created_at < cursor_created_at)
            else:
                # ascending=False (feed/inbox — load mới): lấy records MỚI HƠN cursor
                # (created_at > cursor) OR (created_at == cursor AND id > cursor_id) — tiebreak bằng id
                if cursor_id is not None:
                    stmt = stmt.where(
                        or_(
                            self.model.created_at > cursor_created_at,
                            and_(
                                self.model.created_at == cursor_created_at,
                                self.model.id > cursor_id,
                            ),
                        )
                    )
                else:
                    stmt = stmt.where(self.model.created_at > cursor_created_at)

        if filters:
            stmt = stmt.where(*filters)

        # Order: DESC = mới nhất trước (default), ASC = cũ nhất trước
        if ascending:
            stmt = stmt.order_by(self.model.created_at.asc(), self.model.id.asc()).limit(limit)
        else:
            stmt = stmt.order_by(self.model.created_at.desc(), self.model.id.desc()).limit(limit)

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

        NOTE (C1): updated_at được set tường minh ở đây vì SQLAlchemy onupdate=func.now()
        chỉ hoạt động với Core UPDATE expressions, KHÔNG phải ORM-style setattr+flush.
        """
        valid_columns = {c.key for c in self.model.__table__.columns}
        invalid_keys = set(kwargs.keys()) - valid_columns
        if invalid_keys:
            raise ValueError(
                f"Invalid fields for {self.model.__name__}: {invalid_keys}. "
                f"Valid fields: {valid_columns}"
            )
        # Tự động cập nhật updated_at nếu model có column này
        if "updated_at" in valid_columns and "updated_at" not in kwargs:
            kwargs["updated_at"] = datetime.now(timezone.utc)
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

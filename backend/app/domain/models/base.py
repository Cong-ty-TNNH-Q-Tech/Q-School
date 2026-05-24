"""
Base Mixins — Tái sử dụng cho tất cả ORM models.
Tuân thủ: Mọi bảng cốt lõi phải có created_at, updated_at và deleted_at (Soft Delete).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    """Primary key UUID v4. PK tự có btree index — không cần index=True."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        # Không thêm index=True — primary key column đã tự có unique btree index trên PostgreSQL
    )


class TimestampMixin:
    """Tự động set created_at khi tạo, updated_at khi cập nhật."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Soft Delete — TUYỆT ĐỐI KHÔNG dùng DELETE thật với dữ liệu người dùng.
    Filter: WHERE deleted_at IS NULL để lấy records còn hoạt động.
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,  # Index để tăng tốc query lọc soft-deleted records
    )

    def soft_delete(self) -> None:
        """Đánh dấu record đã bị xóa mà không xóa khỏi DB."""
        self.deleted_at = datetime.now(timezone.utc)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

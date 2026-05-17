"""
Lesson ORM Model — Bài giảng do Giáo viên tạo (có thể được AI hỗ trợ).
"""
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.domain.models.user import User


class Lesson(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Bảng LESSONS — Giáo án / Bài giảng.
    content: JSONB chứa cấu trúc bài giảng linh hoạt (có thể là slides, sections, etc.)
    """
    __tablename__ = "lessons"

    teacher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,   # nullable=True để SET NULL hoạt động khi giáo viên bị xóa
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(100), nullable=True)
    grade_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    content: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Nội dung giáo án - JSON linh hoạt, có thể chứa sections, objectives, activities",
    )

    # viewonly=True vì User không có back_populates "lessons" — tránh ambiguous relationship
    teacher: Mapped["User"] = relationship("User", foreign_keys=[teacher_id], viewonly=True)

    def __repr__(self) -> str:
        return f"<Lesson id={self.id} title={self.title[:30]}>"

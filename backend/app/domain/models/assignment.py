"""
ClassAssignment ORM Model — Bảng trung gian giao bài cho Lớp học.
"Trái tim" của LMS: Giáo viên phải tạo assignment thì Học sinh mới thấy được Lesson/Quiz.
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, DateTime, func, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.models.base import UUIDMixin

if TYPE_CHECKING:
    from app.domain.models.class_ import Class


class ClassAssignment(Base, UUIDMixin):
    """
    Bảng CLASS_ASSIGNMENTS — Giao bài cho Lớp học.

    resource_type: 'lesson' | 'quiz'
    resource_id: UUID của Lesson hoặc Quiz tương ứng
    unlock_date: Thời điểm mở bài (null = mở ngay)
    due_date: Hạn chót nộp bài
    """
    __tablename__ = "class_assignments"
    __table_args__ = (
        CheckConstraint(
            "resource_type IN ('lesson', 'quiz')",
            name="ck_class_assignments_resource_type"
        ),
        # Index 1: query 'lấy tất cả lớp đã giao quiz/lesson cụ thể'
        Index("ix_class_assignments_resource", "resource_type", "resource_id"),
        # Index 2: query 'bài có hạn nộp sắp đến' — dùng cho reminder jobs
        Index("ix_class_assignments_due_date", "due_date"),
        # Index 3: query 'bài cần mở hôm nay' — dùng cho cron job mở bài tự động
        Index("ix_class_assignments_unlock_date", "unlock_date"),
    )

    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resource_type: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="'lesson' hoặc 'quiz'"
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
        comment="ID của Lesson hoặc Quiz"
    )
    unlock_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Thời gian mở bài. NULL = mở ngay lập tức."
    )
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        comment="Hạn chót nộp bài."
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    class_: Mapped["Class"] = relationship("Class", back_populates="assignments")

    def __repr__(self) -> str:
        return f"<ClassAssignment class={self.class_id} {self.resource_type}={self.resource_id}>"

"""
Class & ClassStudent ORM Models — Lớp học và quan hệ Học sinh/Lớp
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.domain.models.user import User
    from app.domain.models.assignment import ClassAssignment


class Class(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Bảng Classes — Lớp học do Giáo viên quản lý.
    Một lớp thuộc về một giáo viên, có nhiều học sinh qua bảng trung gian.
    """
    __tablename__ = "classes"

    teacher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,   # nullable=True để SET NULL hoạt động khi giáo viên bị xóa
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    grade_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    teacher: Mapped["User"] = relationship(
        "User", back_populates="managed_classes", foreign_keys=[teacher_id]
    )
    students: Mapped[list["ClassStudent"]] = relationship(
        "ClassStudent", back_populates="class_", cascade="all, delete-orphan"
    )
    assignments: Mapped[list["ClassAssignment"]] = relationship(
        "ClassAssignment", back_populates="class_"
    )

    def __repr__(self) -> str:
        return f"<Class id={self.id} name={self.name}>"


class ClassStudent(Base):
    """
    Bảng CLASS_STUDENTS — Bảng trung gian M-N giữa Class và User (Student).
    Composite PK: (class_id, student_id)
    """
    __tablename__ = "class_students"
    # Composite PK (class_id, student_id) — PostgreSQL tự tạo index cho (class_id, student_id)
    # Nhưng cần thêm index riêng cho student_id để query ngược lại (học sinh này đang học lớp nào)

    class_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("classes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,  # Index để query 'học sinh này đang học lớp nào?'
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    class_: Mapped["Class"] = relationship("Class", back_populates="students")
    student: Mapped["User"] = relationship("User", back_populates="class_enrollments")

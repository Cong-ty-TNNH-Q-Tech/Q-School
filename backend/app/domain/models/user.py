"""
User & Profile ORM Models — Group 1: System Core & Authentication
"""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.domain.models.class_ import Class, ClassStudent
    from app.domain.models.ai import ChatSession
    from app.domain.models.billing import UserSubscription


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Bảng Users — Tài khoản hệ thống.
    role: 'student' | 'teacher' | 'admin'
    """
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('student', 'teacher', 'admin')",
            name="ck_users_role"
        ),
    )

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    profile: Mapped["Profile"] = relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    managed_classes: Mapped[list["Class"]] = relationship(
        "Class", back_populates="teacher", foreign_keys="Class.teacher_id"
    )
    class_enrollments: Mapped[list["ClassStudent"]] = relationship(
        "ClassStudent", back_populates="student"
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession", back_populates="user"
    )
    subscriptions: Mapped[list["UserSubscription"]] = relationship(
        "UserSubscription", back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"


class Profile(Base):
    """
    Bảng Profiles — Thông tin bổ sung của User.
    Quan hệ 1-1 với Users, PK chính là user_id.
    """
    __tablename__ = "profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    school_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="Gamification points")

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="profile")

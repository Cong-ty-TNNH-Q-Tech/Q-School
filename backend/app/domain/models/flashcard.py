"""
Flashcard ORM Models — FlashcardSet, Flashcard, FlashcardReview
Hỗ trợ Spaced Repetition (confidence_level + next_review_at).
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.domain.models.user import User


class FlashcardSet(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Bảng FLASHCARD_SETS — Bộ thẻ ghi nhớ."""
    __tablename__ = "flashcard_sets"

    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    flashcards: Mapped[list["Flashcard"]] = relationship(
        "Flashcard", back_populates="set_", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<FlashcardSet id={self.id} title={self.title[:30]}>"


class Flashcard(Base, UUIDMixin):
    """Bảng FLASHCARDS — Thẻ ghi nhớ đơn lẻ (front/back)."""
    __tablename__ = "flashcards"

    set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("flashcard_sets.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    front_text: Mapped[str] = mapped_column(Text, nullable=False)
    back_text: Mapped[str] = mapped_column(Text, nullable=False)
    media_url: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="Ảnh minh họa")

    set_: Mapped["FlashcardSet"] = relationship("FlashcardSet", back_populates="flashcards")
    reviews: Mapped[list["FlashcardReview"]] = relationship(
        "FlashcardReview", back_populates="flashcard", cascade="all, delete-orphan"
    )


class FlashcardReview(Base, UUIDMixin):
    """
    Bảng FLASHCARD_REVIEWS — Theo dõi tiến độ ôn tập của từng Học sinh.
    Spaced Repetition: confidence_level (1-5) quyết định next_review_at.
    """
    __tablename__ = "flashcard_reviews"
    __table_args__ = (
        UniqueConstraint("student_id", "flashcard_id", name="uq_flashcard_review_student_card"),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    flashcard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("flashcards.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    confidence_level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1,
        comment="Mức độ tự tin 1-5 (1=Không nhớ, 5=Thuộc lòng)"
    )
    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    flashcard: Mapped["Flashcard"] = relationship("Flashcard", back_populates="reviews")

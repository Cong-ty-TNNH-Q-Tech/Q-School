"""
Quiz, Question, Answer, Rubric, EssaySubmission, QuizAttempt, StudentAnswer ORM Models
Group 2: EdTech Core & Assignments
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    String,
    Text,
    Boolean,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.domain.models.user import User


class Quiz(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Bảng QUIZZES — Bộ đề trắc nghiệm."""

    __tablename__ = "quizzes"

    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content_source: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Văn bản gốc dùng để AI sinh câu hỏi"
    )

    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="Question.display_order",
    )
    attempts: Mapped[list["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="quiz"
    )

    def __repr__(self) -> str:
        return f"<Quiz id={self.id} title={self.title[:30]}>"


class Question(Base, UUIDMixin):
    """Bảng QUESTIONS — Câu hỏi trong Quiz."""

    __tablename__ = "questions"

    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    media_url: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="Ảnh/Video minh họa"
    )
    explanation: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Giải thích đáp án"
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(
        "Answer", back_populates="question", cascade="all, delete-orphan"
    )
    student_answers: Mapped[list["StudentAnswer"]] = relationship(
        "StudentAnswer", back_populates="question"
    )


class Answer(Base, UUIDMixin):
    """Bảng ANSWERS — Các lựa chọn đáp án cho Question."""

    __tablename__ = "answers"

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    media_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    question: Mapped["Question"] = relationship("Question", back_populates="answers")


class Rubric(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Bảng RUBRICS — Thang điểm chấm bài viết."""

    __tablename__ = "rubrics"

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    criteria_matrix: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict, comment="Ma trận tiêu chí chấm điểm"
    )

    essay_submissions: Mapped[list["EssaySubmission"]] = relationship(
        "EssaySubmission", back_populates="rubric"
    )


class EssaySubmission(Base, UUIDMixin, TimestampMixin):
    """Bảng ESSAY_SUBMISSIONS — Bài văn học sinh nộp + AI feedback."""

    __tablename__ = "essay_submissions"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    rubric_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rubrics.id"), nullable=True
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Nội dung bài văn"
    )
    ai_feedback: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, comment="Nhận xét chi tiết từ AI theo từng tiêu chí"
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)

    rubric: Mapped["Rubric | None"] = relationship(
        "Rubric", back_populates="essay_submissions"
    )


class QuizAttempt(Base, UUIDMixin):
    """Bảng QUIZ_ATTEMPTS — Lịch sử làm bài của Học sinh."""

    __tablename__ = "quiz_attempts"
    # Không có UniqueConstraint(student_id, quiz_id) — học sinh có thể làm lại bài nhiều lần (intentional)

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False, index=True
    )
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="attempts")
    student_answers: Mapped[list["StudentAnswer"]] = relationship(
        "StudentAnswer", back_populates="attempt", cascade="all, delete-orphan"
    )


class StudentAnswer(Base, UUIDMixin):
    """Bảng STUDENT_ANSWERS — Chi tiết từng câu trả lời trong một lượt làm bài."""

    __tablename__ = "student_answers"
    __table_args__ = (
        UniqueConstraint(
            "attempt_id", "question_id", name="uq_student_answer_attempt_question"
        ),
    )

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quiz_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False
    )
    selected_answer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("answers.id"), nullable=True
    )
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    attempt: Mapped["QuizAttempt"] = relationship(
        "QuizAttempt", back_populates="student_answers"
    )
    question: Mapped["Question"] = relationship(
        "Question", back_populates="student_answers"
    )

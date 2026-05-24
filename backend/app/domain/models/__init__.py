"""
Domain Models — Export tập trung tất cả ORM models.
Alembic và main.py import từ đây để đảm bảo metadata đầy đủ khi chạy migration.
"""

from app.domain.models.base import UUIDMixin, TimestampMixin, SoftDeleteMixin
from app.domain.models.user import User, Profile
from app.domain.models.class_ import Class, ClassStudent
from app.domain.models.lesson import Lesson
from app.domain.models.quiz import (
    Quiz,
    Question,
    Answer,
    Rubric,
    EssaySubmission,
    QuizAttempt,
    StudentAnswer,
)
from app.domain.models.flashcard import FlashcardSet, Flashcard, FlashcardReview
from app.domain.models.assignment import ClassAssignment
from app.domain.models.ai import (
    AIPrompt,
    ChatSession,
    ChatMessage,
    Document,
    DocumentChunk,
    AITask,
    GeneratedAsset,
)
from app.domain.models.billing import Plan, UserSubscription, PaymentTransaction

__all__ = [
    # Mixins
    "UUIDMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    # Auth
    "User",
    "Profile",
    # Classes
    "Class",
    "ClassStudent",
    # Content
    "Lesson",
    "Quiz",
    "Question",
    "Answer",
    "Rubric",
    "EssaySubmission",
    "QuizAttempt",
    "StudentAnswer",
    "FlashcardSet",
    "Flashcard",
    "FlashcardReview",
    "ClassAssignment",
    # AI
    "AIPrompt",
    "ChatSession",
    "ChatMessage",
    "Document",
    "DocumentChunk",
    "AITask",
    "GeneratedAsset",
    # Billing
    "Plan",
    "UserSubscription",
    "PaymentTransaction",
]

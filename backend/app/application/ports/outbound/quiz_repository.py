"""
Outbound Port — Repository Interface cho Quiz, Question, Attempt.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.quiz import Quiz, QuizAttempt


class IQuizRepository(ABC):
    """Abstract Port: Contract cho Quiz data access."""

    @abstractmethod
    async def get_by_id(self, quiz_id: UUID) -> Quiz | None: ...

    @abstractmethod
    async def get_by_creator(self, creator_id: UUID) -> list[Quiz]: ...

    @abstractmethod
    async def create(self, creator_id: UUID, title: str, **kwargs) -> Quiz: ...

    @abstractmethod
    async def soft_delete(self, quiz: Quiz) -> Quiz: ...


class IQuizAttemptRepository(ABC):
    """Abstract Port: Contract cho Quiz Attempt data access."""

    @abstractmethod
    async def get_by_id(self, attempt_id: UUID) -> QuizAttempt | None: ...

    @abstractmethod
    async def create(
        self, student_id: UUID, quiz_id: UUID, **kwargs
    ) -> QuizAttempt: ...

    @abstractmethod
    async def complete(self, attempt: QuizAttempt, score: float) -> QuizAttempt: ...

    @abstractmethod
    async def get_by_student_and_quiz(
        self, student_id: UUID, quiz_id: UUID, *, limit: int = 10
    ) -> list[QuizAttempt]:
        """Lấy lịch sử làm bài. limit để tránh load quá nhiều lượt làm lại."""
        ...




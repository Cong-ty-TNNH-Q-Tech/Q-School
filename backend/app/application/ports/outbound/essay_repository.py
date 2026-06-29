"""
Outbound Port — Repository Interface cho Essay Submission.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.quiz import EssaySubmission


class IEssaySubmissionRepository(ABC):
    """Abstract Port: Contract cho Essay Submission data access."""

    @abstractmethod
    async def get_by_id(self, submission_id: UUID) -> EssaySubmission | None: ...

    @abstractmethod
    async def list_by_student(
        self, student_id: UUID, *, cursor: UUID | None = None, limit: int = 20
    ) -> list[EssaySubmission]:
        """Lấy tất cả bài viết của student, giới hạn bằng limit và dùng cursor."""
        ...

    @abstractmethod
    async def create(
        self, student_id: UUID, teacher_id: UUID, content: str, **kwargs
    ) -> EssaySubmission: ...

    @abstractmethod
    async def update_feedback(
        self, submission: EssaySubmission, ai_feedback: dict, score: float
    ) -> EssaySubmission: ...

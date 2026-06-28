from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.quiz_repository import IEssaySubmissionRepository
from app.domain.models.quiz import EssaySubmission


class EssayRepository(BaseRepository[EssaySubmission], IEssaySubmissionRepository):
    """
    Adapter cho bảng ESSAY_SUBMISSIONS.
    Sử dụng BaseRepository(EssaySubmission) để tái sử dụng get_by_id.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(EssaySubmission, db)

    async def get_by_id(self, submission_id: UUID) -> EssaySubmission | None:
        query = select(EssaySubmission).where(EssaySubmission.id == submission_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_student(
        self, student_id: UUID, *, limit: int = 20
    ) -> list[EssaySubmission]:
        query = (
            select(EssaySubmission)
            .where(EssaySubmission.student_id == student_id)
            .order_by(EssaySubmission.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(
        self, student_id: UUID, teacher_id: UUID, content: str, **kwargs
    ) -> EssaySubmission:
        submission = EssaySubmission(
            student_id=student_id,
            teacher_id=teacher_id,
            content=content,
            **kwargs
        )
        self.db.add(submission)
        await self.db.flush()
        return submission

    async def update_feedback(
        self, submission: EssaySubmission, ai_feedback: dict, score: float
    ) -> EssaySubmission:
        submission.ai_feedback = ai_feedback
        submission.score = score
        await self.db.flush()
        return submission

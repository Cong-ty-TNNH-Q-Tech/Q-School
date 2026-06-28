from uuid import UUID
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.quiz_repository import IEssaySubmissionRepository
from app.domain.models.quiz import EssaySubmission

class SQLAlchemyEssaySubmissionRepository(BaseRepository[EssaySubmission], IEssaySubmissionRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(EssaySubmission, session)

    async def get_by_id(self, submission_id: UUID) -> EssaySubmission | None:
        stmt = select(EssaySubmission).options(selectinload(EssaySubmission.rubric)).where(EssaySubmission.id == submission_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_student(self, student_id: UUID, *, limit: int = 20) -> list[EssaySubmission]:
        stmt = select(EssaySubmission).where(EssaySubmission.student_id == student_id).order_by(desc(EssaySubmission.created_at)).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, student_id: UUID, teacher_id: UUID, content: str, **kwargs) -> EssaySubmission:
        submission = EssaySubmission(
            student_id=student_id,
            teacher_id=teacher_id,
            content=content,
            **kwargs
        )
        self.db.add(submission)
        await self.db.flush()
        return submission

    async def update_feedback(self, submission: EssaySubmission, ai_feedback: dict, score: float) -> EssaySubmission:
        submission.ai_feedback = ai_feedback
        submission.score = score
        # The object is attached to the session, so flush will update it.
        await self.db.flush()
        return submission

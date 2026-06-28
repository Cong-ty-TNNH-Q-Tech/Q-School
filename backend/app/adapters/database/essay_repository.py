from uuid import UUID
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.ports.outbound.quiz_repository import IEssaySubmissionRepository
from app.domain.models.quiz import EssaySubmission

class SQLAlchemyEssaySubmissionRepository(IEssaySubmissionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, submission_id: UUID) -> EssaySubmission | None:
        stmt = select(EssaySubmission).options(selectinload(EssaySubmission.rubric)).where(EssaySubmission.id == submission_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_student(self, student_id: UUID, *, limit: int = 20) -> list[EssaySubmission]:
        stmt = select(EssaySubmission).where(EssaySubmission.student_id == student_id).order_by(desc(EssaySubmission.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, student_id: UUID, teacher_id: UUID, content: str, **kwargs) -> EssaySubmission:
        submission = EssaySubmission(
            student_id=student_id,
            teacher_id=teacher_id,
            content=content,
            **kwargs
        )
        self.session.add(submission)
        await self.session.flush()
        return submission

    async def update_feedback(self, submission: EssaySubmission, ai_feedback: dict, score: float) -> EssaySubmission:
        submission.ai_feedback = ai_feedback
        submission.score = score
        # The object is attached to the session, so flush will update it.
        await self.session.flush()
        return submission

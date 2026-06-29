from uuid import UUID
from datetime import datetime
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

    async def list_by_student(
        self,
        student_id: UUID,
        *,
        limit: int = 20,
        cursor_created_at: "datetime | None" = None,
        cursor_id: UUID | None = None,
        ascending: bool = False,
    ) -> list[EssaySubmission]:
        messages = await self.cursor_paginate(
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
            limit=limit,
            filters=[EssaySubmission.student_id == student_id],
            ascending=ascending,
        )
        return list(messages)

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

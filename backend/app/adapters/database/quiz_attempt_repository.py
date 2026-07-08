from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.quiz_repository import IQuizAttemptRepository
from app.domain.models.quiz import QuizAttempt


class QuizAttemptRepository(BaseRepository[QuizAttempt], IQuizAttemptRepository):
    """
    Adapter cho bảng QUIZ_ATTEMPTS.
    Sử dụng BaseRepository(QuizAttempt) để tái sử dụng get_by_id.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(QuizAttempt, db)

    async def get_by_id(self, attempt_id: UUID) -> QuizAttempt | None:
        query = (
            select(QuizAttempt)
            .where(QuizAttempt.id == attempt_id)
            .options(selectinload(QuizAttempt.student_answers))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self, student_id: UUID, quiz_id: UUID, **kwargs
    ) -> QuizAttempt:
        attempt = QuizAttempt(
            student_id=student_id,
            quiz_id=quiz_id,
            started_at=datetime.now(timezone.utc),
            **kwargs
        )
        self.db.add(attempt)
        await self.db.flush()
        return attempt

    async def complete(self, attempt: QuizAttempt, score: float) -> QuizAttempt:
        attempt.score = score
        attempt.completed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return attempt

    async def get_by_student_and_quiz(
        self, student_id: UUID, quiz_id: UUID, *, cursor: UUID | None = None, limit: int = 10
    ) -> list[QuizAttempt]:
        query = (
            select(QuizAttempt)
            .where(QuizAttempt.student_id == student_id)
            .where(QuizAttempt.quiz_id == quiz_id)
            .order_by(QuizAttempt.started_at.desc())
        )
        
        if cursor:
            cursor_entity = await self.get_by_id(cursor)
            if cursor_entity:
                query = query.where(QuizAttempt.started_at < cursor_entity.started_at)

        query = query.limit(limit).options(selectinload(QuizAttempt.student_answers))
        result = await self.db.execute(query)
        return list(result.scalars().all())

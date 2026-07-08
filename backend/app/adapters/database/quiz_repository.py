from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.quiz_repository import IQuizRepository
from app.domain.models.quiz import Quiz

class SQLAlchemyQuizRepository(BaseRepository[Quiz], IQuizRepository):
    """
    Adapter cho bảng QUIZZES.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(Quiz, db)

    async def get_by_id(self, quiz_id: UUID) -> Quiz | None:
        from app.domain.models.quiz import Question # Import here to avoid circular imports if any, or just at top
        query = (
            select(Quiz)
            .where(Quiz.id == quiz_id, Quiz.deleted_at.is_(None))
            .options(
                selectinload(Quiz.questions).selectinload(Question.answers)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_creator(self, creator_id: UUID) -> list[Quiz]:
        query = (
            select(Quiz)
            .where(Quiz.creator_id == creator_id, Quiz.deleted_at.is_(None))
            .order_by(Quiz.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, creator_id: UUID, title: str, **kwargs) -> Quiz:
        quiz = Quiz(creator_id=creator_id, title=title, **kwargs)
        self.db.add(quiz)
        await self.db.flush()
        return quiz

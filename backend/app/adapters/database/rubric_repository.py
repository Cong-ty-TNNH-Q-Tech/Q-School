"""
RubricSQLAlchemyRepository — Concrete implementation của IRubricRepository.
Copy pattern từ UserSQLAlchemyRepository.
"""
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.quiz_repository import IRubricRepository
from app.domain.models.quiz import Rubric


class RubricSQLAlchemyRepository(BaseRepository[Rubric], IRubricRepository):

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Rubric, db)

    async def get_by_id(self, rubric_id: uuid.UUID) -> Rubric | None:
        """Lấy Rubric theo ID, auto-filter soft-deleted (BaseRepository)."""
        return await super().get_by_id(rubric_id)

    async def get_by_teacher(
        self, teacher_id: uuid.UUID, *, limit: int = 100
    ) -> list[Rubric]:
        """Lấy Rubrics của teacher (chưa bị soft-delete), giới hạn bởi limit."""
        stmt = (
            select(Rubric)
            .where(
                Rubric.teacher_id == teacher_id,
                Rubric.deleted_at.is_(None),
            )
            .order_by(Rubric.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self, teacher_id: uuid.UUID, title: str, criteria_matrix: dict
    ) -> Rubric:
        """Tạo Rubric mới."""
        return await super().create(
            teacher_id=teacher_id,
            title=title,
            criteria_matrix=criteria_matrix,
        )

    async def update(self, rubric: Rubric, **kwargs) -> Rubric:
        return await super().update(rubric, **kwargs)

    async def soft_delete(self, rubric: Rubric) -> Rubric:
        return await super().soft_delete(rubric)

"""
Driven Adapter — Concrete SQLAlchemy Repository cho Rubric.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.rubric_repository import IRubricRepository
from app.domain.models.quiz import Rubric


class RubricSQLAlchemyRepository(BaseRepository[Rubric], IRubricRepository):
    """
    Triển khai IRubricRepository bằng SQLAlchemy.
    Kế thừa BaseRepository để tái sử dụng common CRUD logic.
    """

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Rubric, db)

    async def get_by_id(self, rubric_id: UUID) -> Rubric | None:
        """
        Lấy Rubric theo ID.
        Eager load teacher relationship để tránh MissingGreenlet exception khi serialize.
        """
        result = await self.db.execute(
            select(self.model)
            .options(selectinload(self.model.teacher))
            .where(
                self.model.id == rubric_id,
                self.model.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_teacher(self, teacher_id: UUID) -> list[Rubric]:
        """
        Lấy danh sách tất cả ma trận tiêu chí của một giáo viên.
        """
        result = await self.db.execute(
            select(self.model)
            .options(selectinload(self.model.teacher))
            .where(
                self.model.teacher_id == teacher_id,
                self.model.deleted_at.is_(None),
            )
            .order_by(self.model.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(
        self, teacher_id: UUID, title: str, criteria_matrix: dict[str, Any], **kwargs
    ) -> Rubric:
        """Tạo ma trận tiêu chí mới."""
        return await super().create(
            teacher_id=teacher_id, title=title, criteria_matrix=criteria_matrix, **kwargs
        )

    async def update(self, rubric: Rubric, **kwargs) -> Rubric:
        """Cập nhật ma trận tiêu chí."""
        return await super().update(rubric, **kwargs)

    async def soft_delete(self, rubric: Rubric) -> Rubric:
        """Xóa mềm (thiết lập deleted_at)."""
        return await super().soft_delete(rubric)

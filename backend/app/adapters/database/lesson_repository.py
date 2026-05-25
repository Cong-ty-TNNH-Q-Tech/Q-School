"""
LessonSQLAlchemyRepository — Concrete implementation cua ILessonRepository.
Copy pattern tu ClassSQLAlchemyRepository.

Implement day du:
  - get_by_id: eager load teacher
  - get_by_teacher: danh sach bai giang cua giao vien
  - create, update, soft_delete
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.lesson_repository import ILessonRepository
from app.domain.models.lesson import Lesson


class LessonSQLAlchemyRepository(BaseRepository[Lesson], ILessonRepository):
    """
    Concrete Repository: Truy cap DB cho Lesson bang SQLAlchemy Async.
    Ke thua BaseRepository de tai dung CRUD co ban.
    Implement ILessonRepository de Use Cases inject qua interface.
    """

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Lesson, db)

    # ──────────────────────────────────────────────
    # Interface methods (ILessonRepository)
    # ──────────────────────────────────────────────
    async def get_by_id(self, lesson_id: uuid.UUID) -> Lesson | None:
        """
        Lay Lesson theo ID, eager load teacher de tranh N+1.

        DRY note: deleted_at filter duoc viet lai o day (khong goi super()) vi can
        them selectinload vao cung mot SELECT statement. Day la trade-off co y
        duoc document ro rang (giong ClassSQLAlchemyRepository).
        """
        stmt = (
            select(Lesson)
            .options(selectinload(Lesson.teacher))
            .where(
                Lesson.id == lesson_id,
                Lesson.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_teacher(self, teacher_id: uuid.UUID) -> list[Lesson]:
        """
        Lay tat ca bai giang cua mot giao vien.
        Sap xep theo created_at DESC (moi nhat truoc).
        Eager load teacher de co thong tin teacher khi serialize.
        """
        stmt = (
            select(Lesson)
            .options(selectinload(Lesson.teacher))
            .where(
                Lesson.teacher_id == teacher_id,
                Lesson.deleted_at.is_(None),
            )
            .order_by(Lesson.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        teacher_id: uuid.UUID,
        title: str,
        **kwargs,
    ) -> Lesson:
        """
        Tao bai giang moi.
        kwargs: subject, grade_level, content (JSONB) — tat ca optional.
        """
        lesson = Lesson(
            teacher_id=teacher_id,
            title=title.strip(),
            **kwargs,
        )
        self.db.add(lesson)
        await self.db.flush()
        await self.db.refresh(lesson)
        return lesson

    async def update(self, lesson: Lesson, **kwargs) -> Lesson:
        """Delegate len BaseRepository.update() — tu dong set updated_at."""
        return await super().update(lesson, **kwargs)

    async def soft_delete(self, lesson: Lesson) -> Lesson:
        """Delegate len BaseRepository.soft_delete() — set deleted_at = now()."""
        return await super().soft_delete(lesson)

"""
RubricUseCase — Business logic cho CRUD Rubric.
Pattern copy từ AuthUseCase.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.application.ports.outbound.quiz_repository import IRubricRepository
from app.domain.exceptions import RubricNotFoundError

if TYPE_CHECKING:
    from app.domain.models.quiz import Rubric


class RubricUseCase:
    """
    Use Case: CRUD thang điểm chấm bài viết.
    Inject IRubricRepository qua constructor (Dependency Inversion).
    KHÔNG import FastAPI, KHÔNG import SQLAlchemy.
    """

    def __init__(self, rubric_repo: IRubricRepository) -> None:
        self._repo = rubric_repo

    async def create_rubric(
        self, teacher_id: uuid.UUID, title: str, criteria_matrix: dict
    ) -> "Rubric":
        """Tạo Rubric mới cho teacher."""
        return await self._repo.create(
            teacher_id=teacher_id,
            title=title,
            criteria_matrix=criteria_matrix,
        )

    async def list_teacher_rubrics(self, teacher_id: uuid.UUID) -> list["Rubric"]:
        """Lấy danh sách rubrics của teacher."""
        return await self._repo.get_by_teacher(teacher_id)

    async def get_rubric(self, rubric_id: uuid.UUID, user_id: uuid.UUID) -> "Rubric":
        """
        Lấy rubric theo ID. Kiểm tra ownership.
        Raises:
            RubricNotFoundError: Không tìm thấy hoặc không phải owner.
        """
        rubric = await self._repo.get_by_id(rubric_id)
        if rubric is None:
            raise RubricNotFoundError("Không tìm thấy rubric")
        # NOTE: trả về 404 thay vì 403 để tránh information leakage
        if rubric.teacher_id != user_id:
            raise RubricNotFoundError("Không tìm thấy rubric")
        return rubric

    async def update_rubric(
        self, rubric_id: uuid.UUID, teacher_id: uuid.UUID, **kwargs
    ) -> "Rubric":
        """
        Cập nhật rubric. Chỉ owner mới được sửa.
        Raises:
            RubricNotFoundError
        """
        rubric = await self.get_rubric(rubric_id, teacher_id)
        return await self._repo.update(rubric, **kwargs)

    async def delete_rubric(
        self, rubric_id: uuid.UUID, teacher_id: uuid.UUID
    ) -> "Rubric":
        """
        Soft delete rubric. Chỉ owner mới được xóa.
        Raises:
            RubricNotFoundError
        """
        rubric = await self.get_rubric(rubric_id, teacher_id)
        return await self._repo.soft_delete(rubric)

"""
Rubric Use Case — Application Core.
Chứa business logic cho ma trận tiêu chí chấm điểm.
"""

import logging
from typing import Any
from uuid import UUID

from app.application.ports.outbound.rubric_repository import IRubricRepository
from app.domain.exceptions import RubricNotFoundError, PermissionDeniedError
from app.domain.models.quiz import Rubric
from app.domain.models.user import User

logger = logging.getLogger(__name__)


class RubricUseCase:
    """Business logic cho Rubric."""

    def __init__(self, rubric_repo: IRubricRepository):
        self.rubric_repo = rubric_repo

    async def create_rubric(
        self, teacher: User, title: str, criteria_matrix: dict[str, Any]
    ) -> Rubric:
        """Tạo ma trận tiêu chí mới cho giáo viên."""
        logger.info(f"Teacher {teacher.id} tao rubric moi: {title}")
        rubric = await self.rubric_repo.create(
            teacher_id=teacher.id,
            title=title,
            criteria_matrix=criteria_matrix,
        )
        
        # Reload de eager load teacher relationship (tranh MissingGreenlet)
        reloaded = await self.rubric_repo.get_by_id(rubric.id)
        if not reloaded:
            raise RubricNotFoundError("Loi he thong: Khong the load rubric vua tao.")
        return reloaded

    async def list_teacher_rubrics(self, teacher: User) -> list[Rubric]:
        """Lấy danh sách tất cả ma trận tiêu chí của một giáo viên."""
        logger.info(f"Lay danh sach rubric cho teacher {teacher.id}")
        return await self.rubric_repo.get_by_teacher(teacher.id)

    async def get_rubric(self, rubric_id: UUID) -> Rubric:
        """Lấy thông tin chi tiết rubric theo ID."""
        rubric = await self.rubric_repo.get_by_id(rubric_id)
        if not rubric:
            raise RubricNotFoundError("Khong tim thay ma tran tieu chi.")
        return rubric

    async def update_rubric(
        self, rubric_id: UUID, current_user: User, **fields
    ) -> Rubric:
        """Cập nhật rubric. Teacher chỉ được sửa rubric của mình (admin bypass)."""
        rubric = await self.get_rubric(rubric_id)

        # Ownership check
        if current_user.role != "admin" and rubric.teacher_id != current_user.id:
            logger.warning(
                f"User {current_user.id} thu update rubric {rubric_id} cua nguoi khac."
            )
            raise PermissionDeniedError("Ban khong co quyen sua ma tran tieu chi nay.")

        logger.info(f"Update rubric {rubric_id} voi fields: {fields.keys()}")
        updated = await self.rubric_repo.update(rubric, **fields)

        # Reload voi eager loading de tranh MissingGreenlet khi serialize teacher.
        reloaded = await self.rubric_repo.get_by_id(updated.id)
        if not reloaded:
            raise RubricNotFoundError("Loi he thong: khong the reload rubric sau khi update.")
        return reloaded

    async def delete_rubric(self, rubric_id: UUID, current_user: User) -> None:
        """Xóa mềm rubric. Teacher chỉ được xóa rubric của mình (admin bypass)."""
        rubric = await self.get_rubric(rubric_id)

        # Ownership check
        if current_user.role != "admin" and rubric.teacher_id != current_user.id:
            logger.warning(
                f"User {current_user.id} thu xoa rubric {rubric_id} cua nguoi khac."
            )
            raise PermissionDeniedError("Ban khong co quyen xoa ma tran tieu chi nay.")

        logger.info(f"Soft delete rubric {rubric_id}")
        await self.rubric_repo.soft_delete(rubric)

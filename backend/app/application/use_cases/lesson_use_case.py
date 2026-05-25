"""
LessonUseCase — Business logic cho Lesson module.
Copy pattern tu ClassUseCase.

Nguyen tac Use Case trong Hexagonal Architecture:
  - Nhan INPUT tu Router (primitive types hoac Pydantic models)
  - Goi PORT (ILessonRepository) de truy cap data
  - KHONG goi SQLAlchemy truc tiep, KHONG raise HTTP exceptions
  - Raise DOMAIN EXCEPTIONS khi business rule vi pham
  - Tra ve DOMAIN OBJECTS

Authorization Rules:
  - create_lesson: TeacherDep (teacher hoac admin)
  - update_lesson / delete_lesson: teacher chi sua/xoa bai giang minh, admin bypass
  - get_lesson / list_teacher_lessons: bat ky authenticated user
"""
import uuid
from typing import Any

from app.application.ports.outbound.lesson_repository import ILessonRepository
from app.domain.exceptions import (
    LessonNotFoundError,
    PermissionDeniedError,
)
from app.domain.models.lesson import Lesson
from app.domain.models.user import User


class LessonUseCase:
    """
    Use Case: Xu ly toan bo luong nghiep vu Lesson.
    Inject ILessonRepository qua constructor (Dependency Inversion).

    KHONG import FastAPI, KHONG import SQLAlchemy, KHONG import HTTP exceptions o day.
    """

    def __init__(self, lesson_repo: ILessonRepository) -> None:
        self._repo = lesson_repo

    # ──────────────────────────────────────────────
    # Create
    # ──────────────────────────────────────────────
    async def create_lesson(
        self,
        teacher: User,
        title: str,
        subject: str | None = None,
        grade_level: str | None = None,
        content: dict[str, Any] | None = None,
    ) -> Lesson:
        """
        Tao bai giang moi.
        Chi teacher/admin moi co the tao (enforce boi TeacherDep o Router).
        teacher_id = user dang dang nhap.

        Returns:
            Lesson: Domain object vua tao.
        """
        kwargs: dict[str, Any] = {}
        if subject is not None:
            kwargs["subject"] = subject
        if grade_level is not None:
            kwargs["grade_level"] = grade_level
        if content is not None:
            kwargs["content"] = content

        lesson = await self._repo.create(
            teacher_id=teacher.id,
            title=title,
            **kwargs,
        )

        # NOTE: repo.create() uses flush()+refresh() which does NOT eager-load
        # the teacher relationship. Must reload via get_by_id() which uses
        # selectinload(Lesson.teacher) to avoid MissingGreenlet or null teacher_name.
        reloaded = await self._repo.get_by_id(lesson.id)
        if reloaded is None:
            # Should never happen — just created it
            return lesson
        return reloaded

    # ──────────────────────────────────────────────
    # Read
    # ──────────────────────────────────────────────
    async def get_lesson(self, lesson_id: uuid.UUID) -> Lesson:
        """
        Lay thong tin chi tiet mot bai giang.

        Raises:
            LessonNotFoundError: Khong tim thay bai giang hoac da bi xoa.
        """
        lesson = await self._repo.get_by_id(lesson_id)
        if lesson is None:
            raise LessonNotFoundError(f"Khong tim thay bai giang voi ID: {lesson_id}")
        return lesson

    async def list_teacher_lessons(self, teacher: User) -> list[Lesson]:
        """
        Lay danh sach tat ca bai giang do giao vien nay tao.

        Returns:
            list[Lesson]: Danh sach bai giang, sap xep moi nhat truoc.
        """
        return await self._repo.get_by_teacher(teacher.id)

    # ──────────────────────────────────────────────
    # Update
    # ──────────────────────────────────────────────
    async def update_lesson(
        self,
        lesson_id: uuid.UUID,
        current_user: User,
        title: str | None = None,
        subject: str | None = None,
        grade_level: str | None = None,
        content: dict[str, Any] | None = None,
    ) -> Lesson:
        """
        Cap nhat thong tin bai giang (partial update).
        Teacher chi duoc sua bai giang cua minh. Admin bypass ownership check.

        Raises:
            LessonNotFoundError: Khong tim thay bai giang.
            PermissionDeniedError: Teacher co sua bai giang cua nguoi khac.
        """
        lesson = await self._repo.get_by_id(lesson_id)
        if lesson is None:
            raise LessonNotFoundError(f"Khong tim thay bai giang voi ID: {lesson_id}")

        # Ownership check: admin bypass, teacher chi sua bai giang minh
        if current_user.role != "admin" and lesson.teacher_id != current_user.id:
            raise PermissionDeniedError("Ban khong co quyen chinh sua bai giang nay")

        # Chi update cac field duoc truyen vao (partial update)
        update_kwargs: dict[str, Any] = {}
        if title is not None:
            update_kwargs["title"] = title
        if subject is not None:
            update_kwargs["subject"] = subject
        if grade_level is not None:
            update_kwargs["grade_level"] = grade_level
        if content is not None:
            update_kwargs["content"] = content

        if not update_kwargs:
            return lesson  # Khong co gi can update

        updated = await self._repo.update(lesson, **update_kwargs)

        # Reload voi eager loading de tranh MissingGreenlet khi serialize teacher.
        reloaded = await self._repo.get_by_id(updated.id)
        if reloaded is None:
            raise LessonNotFoundError(f"Loi internal: khong the reload bai giang {lesson_id}")
        return reloaded

    # ──────────────────────────────────────────────
    # Delete
    # ──────────────────────────────────────────────
    async def delete_lesson(
        self,
        lesson_id: uuid.UUID,
        current_user: User,
    ) -> None:
        """
        Soft delete bai giang.
        Teacher chi duoc xoa bai giang cua minh. Admin bypass ownership check.

        Raises:
            LessonNotFoundError: Khong tim thay bai giang.
            PermissionDeniedError: Teacher co xoa bai giang cua nguoi khac.
        """
        lesson = await self._repo.get_by_id(lesson_id)
        if lesson is None:
            raise LessonNotFoundError(f"Khong tim thay bai giang voi ID: {lesson_id}")

        # Ownership check
        if current_user.role != "admin" and lesson.teacher_id != current_user.id:
            raise PermissionDeniedError("Ban khong co quyen xoa bai giang nay")

        await self._repo.soft_delete(lesson)

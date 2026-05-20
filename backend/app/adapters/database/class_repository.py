"""
ClassSQLAlchemyRepository — Concrete implementation của IClassRepository.
Copy pattern từ UserSQLAlchemyRepository.

Implement đầy đủ:
  - get_by_id: eager load students + teacher
  - get_by_teacher: lấy danh sách lớp của giáo viên
  - create, update, soft_delete
  - add_student, remove_student (kiểm tra enrollment)
  - get_students
"""
import uuid

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.class_repository import IClassRepository
from app.domain.models.class_ import Class, ClassStudent


class ClassSQLAlchemyRepository(BaseRepository[Class], IClassRepository):
    """
    Concrete Repository: Truy cập DB cho Class bằng SQLAlchemy Async.
    Kế thừa BaseRepository để tái dụng CRUD cơ bản.
    Implement IClassRepository để Use Cases inject qua interface.
    """

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Class, db)

    # ──────────────────────────────────────────────
    # Interface methods (IClassRepository)
    # ──────────────────────────────────────────────
    async def get_by_id(self, class_id: uuid.UUID) -> Class | None:
        """
        Lấy Class theo ID.
        Eager load students (ClassStudent) và teacher (User) để tránh N+1.
        """
        stmt = (
            select(Class)
            .options(
                selectinload(Class.students).selectinload(ClassStudent.student),
                selectinload(Class.teacher),
            )
            .where(
                Class.id == class_id,
                Class.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_teacher(self, teacher_id: uuid.UUID) -> list[Class]:
        """
        Lấy tất cả lớp học của một giáo viên.
        Sắp xếp theo created_at DESC (mới nhất trước).
        Eager load students để có student_count.
        """
        stmt = (
            select(Class)
            .options(selectinload(Class.students))
            .where(
                Class.teacher_id == teacher_id,
                Class.deleted_at.is_(None),
            )
            .order_by(Class.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        teacher_id: uuid.UUID,
        name: str,
        **kwargs,
    ) -> Class:
        """
        Tạo lớp học mới.
        kwargs: grade_level, subject (optional).
        """
        class_ = Class(
            teacher_id=teacher_id,
            name=name.strip(),
            **kwargs,
        )
        self.db.add(class_)
        await self.db.flush()
        await self.db.refresh(class_)
        return class_

    async def update(self, class_: Class, **kwargs) -> Class:
        """Delegate lên BaseRepository.update() — tự động set updated_at."""
        return await super().update(class_, **kwargs)

    async def soft_delete(self, class_: Class) -> Class:
        """Delegate lên BaseRepository.soft_delete() — set deleted_at = now()."""
        return await super().soft_delete(class_)

    async def add_student(
        self,
        class_id: uuid.UUID,
        student_id: uuid.UUID,
    ) -> ClassStudent:
        """
        Thêm học sinh vào lớp.
        Caller phải kiểm tra StudentAlreadyEnrolledError trước khi gọi.
        """
        enrollment = ClassStudent(
            class_id=class_id,
            student_id=student_id,
        )
        self.db.add(enrollment)
        await self.db.flush()
        await self.db.refresh(enrollment)
        return enrollment

    async def remove_student(
        self,
        class_id: uuid.UUID,
        student_id: uuid.UUID,
    ) -> None:
        """
        Xóa học sinh khỏi lớp (hard delete cho bảng trung gian M-N).
        ClassStudent không có deleted_at — đây là dữ liệu quan hệ, không phải user data.
        """
        stmt = delete(ClassStudent).where(
            ClassStudent.class_id == class_id,
            ClassStudent.student_id == student_id,
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def get_students(self, class_id: uuid.UUID) -> list[ClassStudent]:
        """
        Lấy danh sách học sinh của một lớp.
        Eager load User để có username, email.
        Sắp xếp theo joined_at ASC.
        """
        stmt = (
            select(ClassStudent)
            .options(selectinload(ClassStudent.student))
            .where(ClassStudent.class_id == class_id)
            .order_by(ClassStudent.joined_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ──────────────────────────────────────────────
    # Extra helper queries
    # ──────────────────────────────────────────────
    async def is_student_enrolled(
        self,
        class_id: uuid.UUID,
        student_id: uuid.UUID,
    ) -> bool:
        """Kiểm tra học sinh đã tham gia lớp này chưa."""
        stmt = select(ClassStudent.student_id).where(
            ClassStudent.class_id == class_id,
            ClassStudent.student_id == student_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

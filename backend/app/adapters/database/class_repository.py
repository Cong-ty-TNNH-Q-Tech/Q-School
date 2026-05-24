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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.class_repository import IClassRepository
from app.domain.exceptions import StudentAlreadyEnrolledError
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
        Lấy Class theo ID, eager load students + teacher để tránh N+1.

        DRY note: deleted_at filter được viết lại ở đây (không gọi super()) vì cần
        thêm selectinload vào cùng một SELECT statement. SQLAlchemy không cho phép
        thêm options() sau khi query đã cấu hình bởi super(). Đây là trade-off cố
        ý được document rõ ràng.
        """
        stmt = (
            select(Class)
            .options(
                selectinload(Class.students).selectinload(ClassStudent.student),
                selectinload(Class.teacher),
            )
            .where(
                Class.id == class_id,
                Class.deleted_at.is_(None),  # duplicate từ BaseRepository.get_by_id
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

        Race condition guard: Nếu hai request concurrent cùng vượt qua kiểm tra
        in-memory trong UseCase và cùng insert, PK (class_id, student_id) sẽ
        raise IntegrityError. Bắt trong SAVEPOINT để không rollback toàn bộ
        transaction bao ngoài (quan trọng cho cả production lẫn test isolation).
        """
        enrollment = ClassStudent(
            class_id=class_id,
            student_id=student_id,
        )
        self.db.add(enrollment)
        try:
            # begin_nested() tạo SAVEPOINT riêng — chỉ rollback phần insert này
            # nếu PK violation, không ảnh hưởng transaction bao ngoài.
            async with self.db.begin_nested():
                await self.db.flush()
        except IntegrityError:
            raise StudentAlreadyEnrolledError(
                "Học sinh này đã được thêm vào lớp học (concurrent request)"
            )
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

    # ──────────────────────────────────────────────
    # Extra helper (ngoài IClassRepository interface)
    # ──────────────────────────────────────────────
    async def get_students(self, class_id: uuid.UUID) -> list[ClassStudent]:
        """
        Lấy danh sách học sinh của một lớp.
        Eager load User để có username, email. Sắp xếp theo joined_at ASC.

        ISP note: Method này KHÔNG nằm trong IClassRepository vì ClassUseCase
        dùng class_.students đã eager-loaded từ get_by_id(), không cần extra query.
        Giữ lại ở đây cho future use cases có thể cần.

        SRP note: is_student_enrolled() đã bị xóa — logic kiểm tra duplicate
        được thực hiện in-memory trong UseCase (dùng enrolled_ids set từ eager load),
        hiệu quả hơn một round-trip DB bổ sung.
        """
        stmt = (
            select(ClassStudent)
            .options(selectinload(ClassStudent.student))
            .where(ClassStudent.class_id == class_id)
            .order_by(ClassStudent.joined_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

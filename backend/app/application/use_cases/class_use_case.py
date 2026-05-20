"""
ClassUseCase — Business logic cho Class module.
Copy pattern từ AuthUseCase.

Nguyên tắc Use Case trong Hexagonal Architecture:
  - Nhận INPUT từ Router (primitive types hoặc Pydantic models)
  - Gọi PORT (IClassRepository) để truy cập data — KHÔNG gọi SQLAlchemy trực tiếp
  - Raise DOMAIN EXCEPTIONS khi business rule vi phạm
  - Trả về DOMAIN OBJECTS

Authorization Rules:
  - create_class: TeacherDep (teacher hoặc admin)
  - update_class / delete_class: teacher chỉ sửa/xóa lớp mình, admin bypass
  - enroll_student / remove_student: teacher ownership check hoặc admin
  - list_teacher_classes / get_class: bất kỳ authenticated user
"""
import uuid

from app.application.ports.outbound.class_repository import IClassRepository
from app.domain.exceptions import (
    ClassNotFoundError,
    StudentAlreadyEnrolledError,
    NotEnrolledError,
    UserNotFoundError,
)
from app.domain.models.class_ import Class, ClassStudent
from app.domain.models.user import User
from app.core.exceptions import ForbiddenException


class ClassUseCase:
    """
    Use Case: Xử lý toàn bộ luồng nghiệp vụ Class.
    Inject IClassRepository qua constructor (Dependency Inversion).

    KHÔNG import FastAPI, KHÔNG import SQLAlchemy ở đây.
    """

    def __init__(self, class_repo: IClassRepository) -> None:
        self._repo = class_repo

    # ──────────────────────────────────────────────
    # Create
    # ──────────────────────────────────────────────
    async def create_class(
        self,
        teacher: User,
        name: str,
        grade_level: str | None = None,
        subject: str | None = None,
    ) -> Class:
        """
        Tạo lớp học mới.
        Chỉ teacher/admin mới có thể tạo lớp (enforce bởi TeacherDep ở Router).
        teacher_id = user đang đăng nhập.

        Returns:
            Class: Domain object vừa tạo.
        """
        kwargs: dict = {}
        if grade_level is not None:
            kwargs["grade_level"] = grade_level
        if subject is not None:
            kwargs["subject"] = subject

        class_ = await self._repo.create(
            teacher_id=teacher.id,
            name=name,
            **kwargs,
        )
        return class_

    # ──────────────────────────────────────────────
    # Read
    # ──────────────────────────────────────────────
    async def get_class(self, class_id: uuid.UUID) -> Class:
        """
        Lấy thông tin chi tiết một lớp học (bao gồm danh sách học sinh).

        Raises:
            ClassNotFoundError: Không tìm thấy lớp hoặc đã bị xóa.
        """
        class_ = await self._repo.get_by_id(class_id)
        if class_ is None:
            raise ClassNotFoundError(f"Không tìm thấy lớp học với ID: {class_id}")
        return class_

    async def list_teacher_classes(self, teacher: User) -> list[Class]:
        """
        Lấy danh sách tất cả lớp học do giáo viên này quản lý.
        Admin xem được tất cả (TODO: admin cần all_classes use case riêng).

        Returns:
            list[Class]: Danh sách lớp, sắp xếp mới nhất trước.
        """
        return await self._repo.get_by_teacher(teacher.id)

    # ──────────────────────────────────────────────
    # Update
    # ──────────────────────────────────────────────
    async def update_class(
        self,
        class_id: uuid.UUID,
        current_user: User,
        name: str | None = None,
        grade_level: str | None = None,
        subject: str | None = None,
    ) -> Class:
        """
        Cập nhật thông tin lớp học (partial update).
        Teacher chỉ được sửa lớp của mình. Admin bypass ownership check.

        Raises:
            ClassNotFoundError: Không tìm thấy lớp.
            ForbiddenException: Teacher cố sửa lớp của người khác.
        """
        class_ = await self._repo.get_by_id(class_id)
        if class_ is None:
            raise ClassNotFoundError(f"Không tìm thấy lớp học với ID: {class_id}")

        # Ownership check: admin bypass, teacher chỉ sửa lớp mình
        if current_user.role != "admin" and class_.teacher_id != current_user.id:
            raise ForbiddenException("Bạn không có quyền chỉnh sửa lớp học này")

        # Chỉ update các field được truyền vào (partial update)
        update_kwargs: dict = {}
        if name is not None:
            update_kwargs["name"] = name
        if grade_level is not None:
            update_kwargs["grade_level"] = grade_level
        if subject is not None:
            update_kwargs["subject"] = subject

        if not update_kwargs:
            return class_  # Không có gì cần update

        return await self._repo.update(class_, **update_kwargs)

    # ──────────────────────────────────────────────
    # Delete
    # ──────────────────────────────────────────────
    async def delete_class(
        self,
        class_id: uuid.UUID,
        current_user: User,
    ) -> None:
        """
        Soft delete lớp học.
        Teacher chỉ được xóa lớp của mình. Admin bypass ownership check.

        Raises:
            ClassNotFoundError: Không tìm thấy lớp.
            ForbiddenException: Teacher cố xóa lớp của người khác.
        """
        class_ = await self._repo.get_by_id(class_id)
        if class_ is None:
            raise ClassNotFoundError(f"Không tìm thấy lớp học với ID: {class_id}")

        # Ownership check
        if current_user.role != "admin" and class_.teacher_id != current_user.id:
            raise ForbiddenException("Bạn không có quyền xóa lớp học này")

        await self._repo.soft_delete(class_)

    # ──────────────────────────────────────────────
    # Student Enrollment
    # ──────────────────────────────────────────────
    async def enroll_student(
        self,
        class_id: uuid.UUID,
        student_id: uuid.UUID,
        current_user: User,
    ) -> ClassStudent:
        """
        Thêm học sinh vào lớp.
        Teacher chỉ được thêm học sinh vào lớp của mình. Admin bypass.

        Raises:
            ClassNotFoundError: Không tìm thấy lớp.
            ForbiddenException: Teacher không có quyền thêm vào lớp người khác.
            StudentAlreadyEnrolledError: Học sinh đã có trong lớp.
        """
        class_ = await self._repo.get_by_id(class_id)
        if class_ is None:
            raise ClassNotFoundError(f"Không tìm thấy lớp học với ID: {class_id}")

        # Ownership check
        if current_user.role != "admin" and class_.teacher_id != current_user.id:
            raise ForbiddenException("Bạn không có quyền thêm học sinh vào lớp này")

        # Kiểm tra học sinh đã tham gia chưa
        # Note: ClassSQLAlchemyRepository có is_student_enrolled(),
        # nhưng IClassRepository không có method này.
        # Ta dùng get_students để check — hoặc sẽ catch IntegrityError tại adapter.
        # Cách sạch hơn: check qua repo method helper (cast về concrete type không được).
        # Giải pháp: thêm is_enrolled vào IClassRepository interface.
        # HIỆN TẠI: check qua get_students (vẫn OK vì eager loaded từ get_by_id).
        enrolled_ids = {e.student_id for e in class_.students}
        if student_id in enrolled_ids:
            raise StudentAlreadyEnrolledError(
                "Học sinh này đã được thêm vào lớp học"
            )

        return await self._repo.add_student(class_id, student_id)

    async def remove_student(
        self,
        class_id: uuid.UUID,
        student_id: uuid.UUID,
        current_user: User,
    ) -> None:
        """
        Xóa học sinh khỏi lớp.
        Teacher chỉ được xóa học sinh khỏi lớp của mình. Admin bypass.

        Raises:
            ClassNotFoundError: Không tìm thấy lớp.
            ForbiddenException: Teacher không có quyền.
            NotEnrolledError: Học sinh chưa tham gia lớp này.
        """
        class_ = await self._repo.get_by_id(class_id)
        if class_ is None:
            raise ClassNotFoundError(f"Không tìm thấy lớp học với ID: {class_id}")

        # Ownership check
        if current_user.role != "admin" and class_.teacher_id != current_user.id:
            raise ForbiddenException("Bạn không có quyền xóa học sinh khỏi lớp này")

        # Kiểm tra học sinh có trong lớp không
        enrolled_ids = {e.student_id for e in class_.students}
        if student_id not in enrolled_ids:
            raise NotEnrolledError("Học sinh này không có trong lớp học")

        await self._repo.remove_student(class_id, student_id)

    async def list_students(
        self,
        class_id: uuid.UUID,
    ) -> list[ClassStudent]:
        """
        Lấy danh sách học sinh của một lớp.

        Raises:
            ClassNotFoundError: Không tìm thấy lớp.
        """
        # Kiểm tra lớp tồn tại trước
        class_ = await self._repo.get_by_id(class_id)
        if class_ is None:
            raise ClassNotFoundError(f"Không tìm thấy lớp học với ID: {class_id}")

        return await self._repo.get_students(class_id)

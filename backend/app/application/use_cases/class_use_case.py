"""
ClassUseCase — Business logic cho Class module.
Copy pattern từ AuthUseCase.

Nguyên tắc Use Case trong Hexagonal Architecture:
  - Nhận INPUT từ Router (primitive types hoặc Pydantic models)
  - Gọi PORT (IClassRepository, IUserRepository) để truy cập data
  - KHÔNG gọi SQLAlchemy trực tiếp, KHÔNG raise HTTP exceptions
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
from app.application.ports.outbound.user_repository import IUserRepository
from app.domain.exceptions import (
    ClassNotFoundError,
    StudentAlreadyEnrolledError,
    NotEnrolledError,
    PermissionDeniedError,
    UserNotFoundError,
)
from app.domain.models.class_ import Class, ClassStudent
from app.domain.models.user import User


class ClassUseCase:
    """
    Use Case: Xử lý toàn bộ luồng nghiệp vụ Class.
    Inject IClassRepository + IUserRepository qua constructor (Dependency Inversion).

    KHÔNG import FastAPI, KHÔNG import SQLAlchemy, KHÔNG import HTTP exceptions ở đây.
    """

    def __init__(
        self,
        class_repo: IClassRepository,
        user_repo: IUserRepository,
    ) -> None:
        self._repo = class_repo
        self._user_repo = user_repo

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
            PermissionDeniedError: Teacher cố sửa lớp của người khác.
        """
        class_ = await self._repo.get_by_id(class_id)
        if class_ is None:
            raise ClassNotFoundError(f"Không tìm thấy lớp học với ID: {class_id}")

        # Ownership check: admin bypass, teacher chỉ sửa lớp mình
        if current_user.role != "admin" and class_.teacher_id != current_user.id:
            raise PermissionDeniedError("Bạn không có quyền chỉnh sửa lớp học này")

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

        updated = await self._repo.update(class_, **update_kwargs)

        # Reload với eager loading để tránh MissingGreenlet khi serialize students.
        # BaseRepository.update() chỉ flush+refresh, không eager load relationships.
        reloaded = await self._repo.get_by_id(updated.id)
        if reloaded is None:
            raise ClassNotFoundError(f"Lỗi internal: không thể reload lớp {class_id}")
        return reloaded

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
            PermissionDeniedError: Teacher cố xóa lớp của người khác.
        """
        class_ = await self._repo.get_by_id(class_id)
        if class_ is None:
            raise ClassNotFoundError(f"Không tìm thấy lớp học với ID: {class_id}")

        # Ownership check
        if current_user.role != "admin" and class_.teacher_id != current_user.id:
            raise PermissionDeniedError("Bạn không có quyền xóa lớp học này")

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
            UserNotFoundError: student_id không tồn tại hoặc không có role 'student'.
            PermissionDeniedError: Teacher không có quyền thêm vào lớp người khác.
            StudentAlreadyEnrolledError: Học sinh đã có trong lớp.
        """
        class_ = await self._repo.get_by_id(class_id)
        if class_ is None:
            raise ClassNotFoundError(f"Không tìm thấy lớp học với ID: {class_id}")

        # Ownership check
        if current_user.role != "admin" and class_.teacher_id != current_user.id:
            raise PermissionDeniedError("Bạn không có quyền thêm học sinh vào lớp này")

        # Validate student tồn tại và có đúng role "student"
        # UserSQLAlchemyRepository.get_by_id đã filter deleted_at IS NULL,
        # nên None kết quả đồng nghĩa với user không tồn tại hoặc đã bị xóa.
        student = await self._user_repo.get_by_id(student_id)
        if student is None:
            raise UserNotFoundError(f"Không tìm thấy học sinh với ID: {student_id}")
        if student.role != "student":
            raise UserNotFoundError(
                f"User với ID {student_id} không phải học sinh (role: {student.role})"
            )

        # Kiểm tra học sinh đã tham gia chưa bằng cách dùng dữ liệu đã eager load.
        # get_by_id đã selectinload(Class.students), nên class_.students đã sẵn sàng.
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
            PermissionDeniedError: Teacher không có quyền.
            NotEnrolledError: Học sinh chưa tham gia lớp này.
        """
        class_ = await self._repo.get_by_id(class_id)
        if class_ is None:
            raise ClassNotFoundError(f"Không tìm thấy lớp học với ID: {class_id}")

        # Ownership check
        if current_user.role != "admin" and class_.teacher_id != current_user.id:
            raise PermissionDeniedError("Bạn không có quyền xóa học sinh khỏi lớp này")

        # Kiểm tra học sinh có trong lớp không — dùng dữ liệu đã eager load
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

        NOTE: get_by_id đã eager load Class.students + ClassStudent.student,
        nên trả về class_.students trực tiếp — tránh double DB query.
        """
        class_ = await self._repo.get_by_id(class_id)
        if class_ is None:
            raise ClassNotFoundError(f"Không tìm thấy lớp học với ID: {class_id}")

        # class_.students đã được eager loaded trong get_by_id,
        # dùng trực tiếp thay vì gọi thêm get_students() (tránh 1 round-trip DB)
        return list(class_.students)

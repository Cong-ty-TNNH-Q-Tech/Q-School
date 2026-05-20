"""
Classes Router — Driving Adapter (Primary).
Copy pattern từ Auth Router.

Nguyên tắc Router trong Hexagonal Architecture:
  1. Nhận HTTP Request → validate bằng Pydantic Schema
  2. Inject dependencies (DbDep, TeacherDep, CurrentUserDep) qua FastAPI Depends
  3. Khởi tạo Use Case với concrete Repository (DI thủ công)
  4. Gọi Use Case → nhận kết quả
  5. Map kết quả → Response Schema → trả về HTTP Response
  6. Map Domain Exception → HTTP Exception (xử lý tại đây, KHÔNG trong Use Case)

Authorization Summary:
  - POST /classes                        → TeacherDep (teacher/admin)
  - GET  /classes                        → TeacherDep (xem lớp của mình)
  - GET  /classes/{id}                   → CurrentUserDep
  - PATCH /classes/{id}                  → TeacherDep (ownership check trong UseCase)
  - DELETE /classes/{id}                 → TeacherDep (ownership check trong UseCase)
  - POST /classes/{id}/students          → TeacherDep (ownership check trong UseCase)
  - DELETE /classes/{id}/students/{sid}  → TeacherDep (ownership check trong UseCase)
  - GET /classes/{id}/students           → CurrentUserDep
"""
import uuid

from fastapi import APIRouter, status

from app.adapters.database.class_repository import ClassSQLAlchemyRepository
from app.application.use_cases.class_use_case import ClassUseCase
from app.core.dependencies import DbDep, CurrentUserDep, TeacherDep
from app.core.exceptions import NotFoundException, ConflictException, ForbiddenException
from app.domain.exceptions import (
    ClassNotFoundError,
    StudentAlreadyEnrolledError,
    NotEnrolledError,
    PermissionDeniedError,
)
from app.domain.models.class_ import Class, ClassStudent
from app.entrypoints.api_v1.schemas import (
    ApiResponse,
    CreateClassRequest,
    UpdateClassRequest,
    EnrollStudentRequest,
    ClassOut,
    ClassDetailOut,
    ClassStudentOut,
)

router = APIRouter()


# ──────────────────────────────────────────────
# Dependency Factory
# ──────────────────────────────────────────────
def get_class_use_case(db: DbDep) -> ClassUseCase:
    """
    Factory function tạo ClassUseCase với concrete ClassRepository.
    Dùng FastAPI Depends để inject vào endpoint.
    """
    repo = ClassSQLAlchemyRepository(db)
    return ClassUseCase(repo)


# ──────────────────────────────────────────────
# Helper: Map Class ORM → Response Schemas
# ──────────────────────────────────────────────
def _map_class_out(class_: Class, student_count: int | None = None) -> ClassOut:
    """
    Map Class ORM object sang ClassOut Pydantic schema.

    student_count: Truyền vào khi biết trước (VD: 0 cho lớp mới tạo).
    Nếu None, tính từ len(class_.students) — chỉ dùng khi đã eager loaded.
    """
    count = student_count if student_count is not None else len(class_.students)
    return ClassOut(
        id=class_.id,
        teacher_id=class_.teacher_id,
        name=class_.name,
        grade_level=class_.grade_level,
        subject=class_.subject,
        created_at=class_.created_at,
        updated_at=class_.updated_at,
        student_count=count,
    )


def _map_class_detail_out(class_: Class) -> ClassDetailOut:
    """
    Map Class ORM object sang ClassDetailOut (bao gồm danh sách học sinh).
    Yêu cầu class_.students và ClassStudent.student đã được eager loaded.
    """
    students_out = [
        ClassStudentOut(
            student_id=enrollment.student_id,
            joined_at=enrollment.joined_at,
            username=enrollment.student.username if enrollment.student else None,
            email=enrollment.student.email if enrollment.student else None,
        )
        for enrollment in (class_.students or [])
    ]

    return ClassDetailOut(
        id=class_.id,
        teacher_id=class_.teacher_id,
        name=class_.name,
        grade_level=class_.grade_level,
        subject=class_.subject,
        created_at=class_.created_at,
        updated_at=class_.updated_at,
        student_count=len(students_out),
        students=students_out,
    )


def _map_student_out(enrollment: ClassStudent) -> ClassStudentOut:
    """
    Map ClassStudent ORM → ClassStudentOut schema.
    Yêu cầu enrollment.student đã được eager loaded.
    """
    return ClassStudentOut(
        student_id=enrollment.student_id,
        joined_at=enrollment.joined_at,
        username=enrollment.student.username if enrollment.student else None,
        email=enrollment.student.email if enrollment.student else None,
    )


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────
@router.post(
    "",
    response_model=ApiResponse[ClassOut],
    status_code=status.HTTP_201_CREATED,
    summary="Tạo lớp học mới",
    description="Tạo lớp học mới. Chỉ giáo viên và admin mới được tạo lớp.",
)
async def create_class(
    body: CreateClassRequest,
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[ClassOut]:
    """
    POST /classes
    Security: Bearer token required (Teacher/Admin role)
    """
    use_case = get_class_use_case(db)
    class_ = await use_case.create_class(
        teacher=current_user,
        name=body.name,
        grade_level=body.grade_level,
        subject=body.subject,
    )
    # Lớp mới tạo chắc chắn chưa có học sinh — truyền student_count=0
    # để tránh truy cập class_.students chưa được eager loaded
    return ApiResponse(
        data=_map_class_out(class_, student_count=0),
        message="Tạo lớp học thành công",
    )


@router.get(
    "",
    response_model=ApiResponse[list[ClassOut]],
    status_code=status.HTTP_200_OK,
    summary="Danh sách lớp học của giáo viên",
    description="Lấy danh sách tất cả lớp học do giáo viên đang đăng nhập quản lý.",
)
async def list_my_classes(
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[list[ClassOut]]:
    """
    GET /classes
    Security: Bearer token required (Teacher/Admin role)

    NOTE: get_by_teacher eager loads Class.students để có student_count.
    """
    use_case = get_class_use_case(db)
    classes = await use_case.list_teacher_classes(current_user)
    return ApiResponse(
        data=[_map_class_out(c) for c in classes],
    )


@router.get(
    "/{class_id}",
    response_model=ApiResponse[ClassDetailOut],
    status_code=status.HTTP_200_OK,
    summary="Chi tiết lớp học",
    description="Lấy thông tin chi tiết lớp học, bao gồm danh sách học sinh.",
)
async def get_class(
    class_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DbDep,
) -> ApiResponse[ClassDetailOut]:
    """
    GET /classes/{class_id}
    Security: Bearer token required (any authenticated user)
    """
    use_case = get_class_use_case(db)
    try:
        class_ = await use_case.get_class(class_id)
    except ClassNotFoundError as e:
        raise NotFoundException(str(e))

    return ApiResponse(data=_map_class_detail_out(class_))


@router.patch(
    "/{class_id}",
    response_model=ApiResponse[ClassOut],
    status_code=status.HTTP_200_OK,
    summary="Cập nhật lớp học",
    description="Cập nhật thông tin lớp học. Teacher chỉ được sửa lớp của mình.",
)
async def update_class(
    class_id: uuid.UUID,
    body: UpdateClassRequest,
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[ClassOut]:
    """
    PATCH /classes/{class_id}
    Security: Bearer token required (Teacher/Admin role)
    Business rule: Teacher chỉ được sửa lớp do mình tạo. Admin bypass.
    """
    use_case = get_class_use_case(db)
    try:
        class_ = await use_case.update_class(
            class_id=class_id,
            current_user=current_user,
            name=body.name,
            grade_level=body.grade_level,
            subject=body.subject,
        )
    except ClassNotFoundError as e:
        raise NotFoundException(str(e))
    except PermissionDeniedError as e:
        raise ForbiddenException(str(e))

    return ApiResponse(
        data=_map_class_out(class_),
        message="Cập nhật lớp học thành công",
    )


@router.delete(
    "/{class_id}",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Xóa lớp học",
    description="Soft delete lớp học. Teacher chỉ được xóa lớp của mình.",
)
async def delete_class(
    class_id: uuid.UUID,
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[None]:
    """
    DELETE /classes/{class_id}
    Security: Bearer token required (Teacher/Admin role)
    Business rule: Teacher chỉ được xóa lớp do mình tạo. Admin bypass.
    """
    use_case = get_class_use_case(db)
    try:
        await use_case.delete_class(class_id, current_user)
    except ClassNotFoundError as e:
        raise NotFoundException(str(e))
    except PermissionDeniedError as e:
        raise ForbiddenException(str(e))

    return ApiResponse(data=None, message="Xóa lớp học thành công")


@router.post(
    "/{class_id}/students",
    response_model=ApiResponse[ClassStudentOut],
    status_code=status.HTTP_201_CREATED,
    summary="Thêm học sinh vào lớp",
    description="Thêm một học sinh vào lớp học. Teacher chỉ được thêm vào lớp của mình.",
)
async def enroll_student(
    class_id: uuid.UUID,
    body: EnrollStudentRequest,
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[ClassStudentOut]:
    """
    POST /classes/{class_id}/students
    Security: Bearer token required (Teacher/Admin role)
    """
    use_case = get_class_use_case(db)
    try:
        enrollment = await use_case.enroll_student(
            class_id=class_id,
            student_id=body.student_id,
            current_user=current_user,
        )
    except ClassNotFoundError as e:
        raise NotFoundException(str(e))
    except StudentAlreadyEnrolledError as e:
        raise ConflictException(str(e))
    except PermissionDeniedError as e:
        raise ForbiddenException(str(e))

    return ApiResponse(
        data=ClassStudentOut(
            student_id=enrollment.student_id,
            joined_at=enrollment.joined_at,
        ),
        message="Thêm học sinh vào lớp thành công",
    )


@router.delete(
    "/{class_id}/students/{student_id}",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Xóa học sinh khỏi lớp",
    description="Xóa học sinh khỏi lớp học. Teacher chỉ được xóa khỏi lớp của mình.",
)
async def remove_student(
    class_id: uuid.UUID,
    student_id: uuid.UUID,
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[None]:
    """
    DELETE /classes/{class_id}/students/{student_id}
    Security: Bearer token required (Teacher/Admin role)
    """
    use_case = get_class_use_case(db)
    try:
        await use_case.remove_student(
            class_id=class_id,
            student_id=student_id,
            current_user=current_user,
        )
    except ClassNotFoundError as e:
        raise NotFoundException(str(e))
    except NotEnrolledError as e:
        raise NotFoundException(str(e))
    except PermissionDeniedError as e:
        raise ForbiddenException(str(e))

    return ApiResponse(data=None, message="Xóa học sinh khỏi lớp thành công")


@router.get(
    "/{class_id}/students",
    response_model=ApiResponse[list[ClassStudentOut]],
    status_code=status.HTTP_200_OK,
    summary="Danh sách học sinh trong lớp",
    description="Lấy danh sách tất cả học sinh trong một lớp học.",
)
async def list_students(
    class_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DbDep,
) -> ApiResponse[list[ClassStudentOut]]:
    """
    GET /classes/{class_id}/students
    Security: Bearer token required (any authenticated user)
    """
    use_case = get_class_use_case(db)
    try:
        enrollments = await use_case.list_students(class_id)
    except ClassNotFoundError as e:
        raise NotFoundException(str(e))

    return ApiResponse(
        data=[_map_student_out(e) for e in enrollments],
    )

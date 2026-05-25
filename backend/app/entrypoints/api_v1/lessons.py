"""
Lessons Router — Driving Adapter (Primary).
Copy pattern tu Classes Router.

Nguyen tac Router trong Hexagonal Architecture:
  1. Nhan HTTP Request -> validate bang Pydantic Schema
  2. Inject dependencies (DbDep, TeacherDep, CurrentUserDep) qua FastAPI Depends
  3. Khoi tao Use Case voi concrete Repository (DI thu cong)
  4. Goi Use Case -> nhan ket qua
  5. Map ket qua -> Response Schema -> tra ve HTTP Response
  6. Map Domain Exception -> HTTP Exception (xu ly tai day, KHONG trong Use Case)

Authorization Summary:
  - POST   /lessons           -> TeacherDep (teacher/admin)
  - GET    /lessons           -> TeacherDep (xem bai giang cua minh)
  - GET    /lessons/{id}      -> CurrentUserDep
  - PATCH  /lessons/{id}      -> TeacherDep (ownership check trong UseCase)
  - DELETE /lessons/{id}      -> TeacherDep (ownership check trong UseCase)
"""
import uuid

from fastapi import APIRouter, status

from app.adapters.database.lesson_repository import LessonSQLAlchemyRepository
from app.application.use_cases.lesson_use_case import LessonUseCase
from app.core.dependencies import DbDep, CurrentUserDep, TeacherDep
from app.core.exceptions import NotFoundException, ForbiddenException
from app.domain.exceptions import (
    LessonNotFoundError,
    PermissionDeniedError,
)
from app.domain.models.lesson import Lesson
from app.entrypoints.api_v1.schemas import (
    ApiResponse,
)
from app.entrypoints.api_v1.schemas.lesson import (
    CreateLessonRequest,
    UpdateLessonRequest,
    LessonOut,
)

router = APIRouter()


# ──────────────────────────────────────────────
# Dependency Factory
# ──────────────────────────────────────────────
def get_lesson_use_case(db: DbDep) -> LessonUseCase:
    """
    Factory function tao LessonUseCase voi concrete Repository.
    Don gian hon ClassUseCase — chi can LessonRepository.
    """
    lesson_repo = LessonSQLAlchemyRepository(db)
    return LessonUseCase(lesson_repo)


# ──────────────────────────────────────────────
# Helper: Map Lesson ORM -> Response Schema
# ──────────────────────────────────────────────
def _map_lesson_out(lesson: Lesson) -> LessonOut:
    """
    Map Lesson ORM object sang LessonOut Pydantic schema.
    teacher_name lay tu eager-loaded teacher relationship.
    """
    teacher_name = None
    if lesson.teacher:
        teacher_name = lesson.teacher.username

    return LessonOut(
        id=lesson.id,
        teacher_id=lesson.teacher_id,
        title=lesson.title,
        subject=lesson.subject,
        grade_level=lesson.grade_level,
        content=lesson.content,
        created_at=lesson.created_at,
        updated_at=lesson.updated_at,
        teacher_name=teacher_name,
    )


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────
@router.post(
    "",
    response_model=ApiResponse[LessonOut],
    status_code=status.HTTP_201_CREATED,
    summary="Tao bai giang moi",
    description="Tao bai giang moi. Chi giao vien va admin moi duoc tao.",
)
async def create_lesson(
    body: CreateLessonRequest,
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[LessonOut]:
    """
    POST /lessons
    Security: Bearer token required (Teacher/Admin role)
    """
    use_case = get_lesson_use_case(db)
    lesson = await use_case.create_lesson(
        teacher=current_user,
        title=body.title,
        subject=body.subject,
        grade_level=body.grade_level,
        content=body.content,
    )
    return ApiResponse(
        data=_map_lesson_out(lesson),
        message="Tao bai giang thanh cong",
    )


@router.get(
    "",
    response_model=ApiResponse[list[LessonOut]],
    status_code=status.HTTP_200_OK,
    summary="Danh sach bai giang cua giao vien",
    description="Lay danh sach tat ca bai giang do giao vien dang dang nhap tao.",
)
async def list_my_lessons(
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[list[LessonOut]]:
    """
    GET /lessons
    Security: Bearer token required (Teacher/Admin role)

    NOTE: get_by_teacher eager loads Lesson.teacher de co teacher_name.
    """
    use_case = get_lesson_use_case(db)
    lessons = await use_case.list_teacher_lessons(current_user)
    return ApiResponse(
        data=[_map_lesson_out(l) for l in lessons],
    )


@router.get(
    "/{lesson_id}",
    response_model=ApiResponse[LessonOut],
    status_code=status.HTTP_200_OK,
    summary="Chi tiet bai giang",
    description="Lay thong tin chi tiet bai giang.",
)
async def get_lesson(
    lesson_id: uuid.UUID,
    _current_user: CurrentUserDep,
    db: DbDep,
) -> ApiResponse[LessonOut]:
    """
    GET /lessons/{lesson_id}
    Security: Bearer token required (any authenticated user)
    """
    use_case = get_lesson_use_case(db)
    try:
        lesson = await use_case.get_lesson(lesson_id)
    except LessonNotFoundError as e:
        raise NotFoundException(str(e))

    return ApiResponse(data=_map_lesson_out(lesson))


@router.patch(
    "/{lesson_id}",
    response_model=ApiResponse[LessonOut],
    status_code=status.HTTP_200_OK,
    summary="Cap nhat bai giang",
    description="Cap nhat thong tin bai giang. Teacher chi duoc sua bai giang cua minh.",
)
async def update_lesson(
    lesson_id: uuid.UUID,
    body: UpdateLessonRequest,
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[LessonOut]:
    """
    PATCH /lessons/{lesson_id}
    Security: Bearer token required (Teacher/Admin role)
    Business rule: Teacher chi duoc sua bai giang do minh tao. Admin bypass.
    """
    use_case = get_lesson_use_case(db)
    try:
        lesson = await use_case.update_lesson(
            lesson_id=lesson_id,
            current_user=current_user,
            title=body.title,
            subject=body.subject,
            grade_level=body.grade_level,
            content=body.content,
        )
    except LessonNotFoundError as e:
        raise NotFoundException(str(e))
    except PermissionDeniedError as e:
        raise ForbiddenException(str(e))

    return ApiResponse(
        data=_map_lesson_out(lesson),
        message="Cap nhat bai giang thanh cong",
    )


@router.delete(
    "/{lesson_id}",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Xoa bai giang",
    description="Soft delete bai giang. Teacher chi duoc xoa bai giang cua minh.",
)
async def delete_lesson(
    lesson_id: uuid.UUID,
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[None]:
    """
    DELETE /lessons/{lesson_id}
    Security: Bearer token required (Teacher/Admin role)
    Business rule: Teacher chi duoc xoa bai giang do minh tao. Admin bypass.
    """
    use_case = get_lesson_use_case(db)
    try:
        await use_case.delete_lesson(lesson_id, current_user)
    except LessonNotFoundError as e:
        raise NotFoundException(str(e))
    except PermissionDeniedError as e:
        raise ForbiddenException(str(e))

    return ApiResponse(data=None, message="Xoa bai giang thanh cong")

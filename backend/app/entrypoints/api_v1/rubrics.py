"""
Rubric Router — Driving Adapter (Primary).
Pattern copy từ auth.py.
"""
from uuid import UUID
from fastapi import APIRouter, status

from app.adapters.database.rubric_repository import RubricSQLAlchemyRepository
from app.application.use_cases.rubric_use_case import RubricUseCase
from app.core.dependencies import DbDep, TeacherDep, CurrentUserDep
from app.core.exceptions import NotFoundException, ValidationException
from app.domain.exceptions import RubricNotFoundError
from app.entrypoints.api_v1.schemas import (
    ApiResponse,
    CreateRubricRequest,
    UpdateRubricRequest,
    RubricOut,
)

router = APIRouter()


def get_rubric_use_case(db: DbDep) -> RubricUseCase:
    """
    Factory function để tạo RubricUseCase với concrete RubricRepository.
    Dùng FastAPI Depends để inject vào endpoint.
    """
    repo = RubricSQLAlchemyRepository(db)
    return RubricUseCase(repo)


@router.post(
    "",
    response_model=ApiResponse[RubricOut],
    status_code=status.HTTP_201_CREATED,
    summary="Tạo Rubric mới",
)
async def create_rubric(
    body: CreateRubricRequest,
    teacher: TeacherDep,
    db: DbDep,
) -> ApiResponse[RubricOut]:
    """
    POST /rubrics
    Security: TeacherDep (teacher/admin only)
    """
    use_case = get_rubric_use_case(db)
    rubric = await use_case.create_rubric(
        teacher_id=teacher.id,
        title=body.title,
        criteria_matrix=body.criteria_matrix,
    )
    return ApiResponse(
        data=RubricOut.model_validate(rubric),
        message="Tạo rubric thành công",
    )


@router.get(
    "",
    response_model=ApiResponse[list[RubricOut]],
    status_code=status.HTTP_200_OK,
    summary="Danh sách Rubric của teacher",
)
async def list_rubrics(
    teacher: TeacherDep,
    db: DbDep,
) -> ApiResponse[list[RubricOut]]:
    """
    GET /rubrics
    Security: TeacherDep (teacher/admin only)
    """
    use_case = get_rubric_use_case(db)
    rubrics = await use_case.list_teacher_rubrics(teacher.id)
    return ApiResponse(
        data=[RubricOut.model_validate(r) for r in rubrics],
    )


@router.get(
    "/{rubric_id}",
    response_model=ApiResponse[RubricOut],
    status_code=status.HTTP_200_OK,
    summary="Chi tiết Rubric",
)
async def get_rubric(
    rubric_id: UUID,
    current_user: CurrentUserDep,
    db: DbDep,
) -> ApiResponse[RubricOut]:
    """
    GET /rubrics/{rubric_id}
    Security: CurrentUserDep (any authenticated user)
    """
    use_case = get_rubric_use_case(db)
    try:
        rubric = await use_case.get_rubric(rubric_id, current_user.id)
    except RubricNotFoundError as e:
        raise NotFoundException(str(e))
    return ApiResponse(data=RubricOut.model_validate(rubric))


@router.patch(
    "/{rubric_id}",
    response_model=ApiResponse[RubricOut],
    status_code=status.HTTP_200_OK,
    summary="Cập nhật Rubric",
)
async def update_rubric(
    rubric_id: UUID,
    body: UpdateRubricRequest,
    teacher: TeacherDep,
    db: DbDep,
) -> ApiResponse[RubricOut]:
    """
    PATCH /rubrics/{rubric_id}
    Security: TeacherDep (teacher/admin only)
    """
    use_case = get_rubric_use_case(db)
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise ValidationException("Không có dữ liệu cập nhật")
    try:
        rubric = await use_case.update_rubric(
            rubric_id=rubric_id,
            teacher_id=teacher.id,
            **update_data,
        )
    except RubricNotFoundError as e:
        raise NotFoundException(str(e))
    return ApiResponse(
        data=RubricOut.model_validate(rubric),
        message="Cập nhật rubric thành công",
    )


@router.delete(
    "/{rubric_id}",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Xóa Rubric (Soft Delete)",
)
async def delete_rubric(
    rubric_id: UUID,
    teacher: TeacherDep,
    db: DbDep,
) -> ApiResponse[None]:
    """
    DELETE /rubrics/{rubric_id}
    Security: TeacherDep (teacher/admin only)
    """
    use_case = get_rubric_use_case(db)
    try:
        await use_case.delete_rubric(rubric_id, teacher.id)
    except RubricNotFoundError as e:
        raise NotFoundException(str(e))
    return ApiResponse(data=None, message="Xóa rubric thành công")

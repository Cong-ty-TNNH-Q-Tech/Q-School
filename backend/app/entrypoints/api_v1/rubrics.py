"""
Rubrics Router — Driving Adapter (Primary).
"""

import uuid

from fastapi import APIRouter, status

from app.adapters.database.rubric_repository import RubricSQLAlchemyRepository
from app.application.use_cases.rubric_use_case import RubricUseCase
from app.core.dependencies import DbDep, CurrentUserDep, TeacherDep
from app.core.exceptions import NotFoundException, ForbiddenException
from app.domain.exceptions import (
    RubricNotFoundError,
    PermissionDeniedError,
)
from app.domain.models.quiz import Rubric
from app.entrypoints.api_v1.schemas import (
    ApiResponse,
)
from app.entrypoints.api_v1.schemas.rubric import (
    CreateRubricRequest,
    UpdateRubricRequest,
    RubricResponse,
)

router = APIRouter()


# ──────────────────────────────────────────────
# Dependency Factory
# ──────────────────────────────────────────────
def get_rubric_use_case(db: DbDep) -> RubricUseCase:
    """
    Factory function tao RubricUseCase voi concrete Repository.
    """
    rubric_repo = RubricSQLAlchemyRepository(db)
    return RubricUseCase(rubric_repo)


# ──────────────────────────────────────────────
# Helper: Map Rubric ORM -> Response Schema
# ──────────────────────────────────────────────
def _map_rubric_out(rubric: Rubric) -> RubricResponse:
    """
    Map Rubric ORM object sang RubricResponse Pydantic schema.
    teacher_name lay tu eager-loaded teacher relationship.
    """
    teacher_name = None
    if rubric.teacher:
        teacher_name = rubric.teacher.username

    return RubricResponse(
        id=rubric.id,
        teacher_id=rubric.teacher_id,
        title=rubric.title,
        criteria_matrix=rubric.criteria_matrix,
        created_at=rubric.created_at,
        updated_at=rubric.updated_at,
        teacher_name=teacher_name,
    )


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────
@router.post(
    "",
    response_model=ApiResponse[RubricResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Tao ma tran tieu chi moi",
    description="Tao ma tran tieu chi moi. Chi giao vien va admin moi duoc tao.",
)
async def create_rubric(
    body: CreateRubricRequest,
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[RubricResponse]:
    """
    POST /rubrics
    Security: Bearer token required (Teacher/Admin role)
    """
    use_case = get_rubric_use_case(db)
    rubric = await use_case.create_rubric(
        teacher=current_user,
        title=body.title,
        criteria_matrix=body.criteria_matrix,
    )
    return ApiResponse(
        data=_map_rubric_out(rubric),
        message="Tao ma tran tieu chi thanh cong",
    )


@router.get(
    "",
    response_model=ApiResponse[list[RubricResponse]],
    status_code=status.HTTP_200_OK,
    summary="Danh sach ma tran tieu chi cua giao vien",
    description="Lay danh sach tat ca ma tran tieu chi do giao vien dang dang nhap tao.",
)
async def list_my_rubrics(
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[list[RubricResponse]]:
    """
    GET /rubrics
    Security: Bearer token required (Teacher/Admin role)
    """
    use_case = get_rubric_use_case(db)
    rubrics = await use_case.list_teacher_rubrics(current_user)
    return ApiResponse(
        data=[_map_rubric_out(r) for r in rubrics],
    )


@router.get(
    "/{rubric_id}",
    response_model=ApiResponse[RubricResponse],
    status_code=status.HTTP_200_OK,
    summary="Chi tiet ma tran tieu chi",
    description="Lay thong tin chi tiet ma tran tieu chi.",
)
async def get_rubric(
    rubric_id: uuid.UUID,
    _current_user: CurrentUserDep,
    db: DbDep,
) -> ApiResponse[RubricResponse]:
    """
    GET /rubrics/{rubric_id}
    Security: Bearer token required (any authenticated user)
    """
    use_case = get_rubric_use_case(db)
    try:
        rubric = await use_case.get_rubric(rubric_id)
    except RubricNotFoundError as e:
        raise NotFoundException(str(e))

    return ApiResponse(data=_map_rubric_out(rubric))


@router.patch(
    "/{rubric_id}",
    response_model=ApiResponse[RubricResponse],
    status_code=status.HTTP_200_OK,
    summary="Cap nhat ma tran tieu chi",
    description="Cap nhat thong tin ma tran tieu chi. Teacher chi duoc sua rubric cua minh.",
)
async def update_rubric(
    rubric_id: uuid.UUID,
    body: UpdateRubricRequest,
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[RubricResponse]:
    """
    PATCH /rubrics/{rubric_id}
    Security: Bearer token required (Teacher/Admin role)
    """
    use_case = get_rubric_use_case(db)
    
    # Loai bo cac field None tu body
    update_data = body.model_dump(exclude_unset=True)
    
    try:
        rubric = await use_case.update_rubric(
            rubric_id=rubric_id,
            current_user=current_user,
            **update_data
        )
    except RubricNotFoundError as e:
        raise NotFoundException(str(e))
    except PermissionDeniedError as e:
        raise ForbiddenException(str(e))

    return ApiResponse(
        data=_map_rubric_out(rubric),
        message="Cap nhat ma tran tieu chi thanh cong",
    )


@router.delete(
    "/{rubric_id}",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Xoa ma tran tieu chi",
    description="Soft delete ma tran tieu chi. Teacher chi duoc xoa rubric cua minh.",
)
async def delete_rubric(
    rubric_id: uuid.UUID,
    current_user: TeacherDep,
    db: DbDep,
) -> ApiResponse[None]:
    """
    DELETE /rubrics/{rubric_id}
    Security: Bearer token required (Teacher/Admin role)
    """
    use_case = get_rubric_use_case(db)
    try:
        await use_case.delete_rubric(rubric_id, current_user)
    except RubricNotFoundError as e:
        raise NotFoundException(str(e))
    except PermissionDeniedError as e:
        raise ForbiddenException(str(e))

    return ApiResponse(data=None, message="Xoa ma tran tieu chi thanh cong")

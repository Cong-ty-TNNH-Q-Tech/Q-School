import uuid

from fastapi import APIRouter, Depends, status

from app.core.dependencies import DbDep, CurrentUserDep, AIUserDep
from app.core.exceptions import NotFoundException, ForbiddenException
import logging

logger = logging.getLogger(__name__)
from app.adapters.database.essay_repository import EssayRepository
from app.adapters.database.ai_repository import SQLAlchemyAITaskRepository
from app.application.use_cases.essay_use_case import EssayUseCase
from app.entrypoints.api_v1.schemas import ApiResponse
from app.entrypoints.api_v1.schemas.essay import (
    EssaySubmissionRequest,
    EssaySubmissionResponse,
    EssaySubmissionAcceptedResponse,
)

router = APIRouter()

def get_essay_use_case(db: DbDep) -> EssayUseCase:
    essay_repo = EssayRepository(db)
    ai_task_repo = SQLAlchemyAITaskRepository(db)
    return EssayUseCase(essay_repo=essay_repo, ai_task_repo=ai_task_repo)

@router.post(
    "",
    response_model=ApiResponse[EssaySubmissionAcceptedResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Nộp bài tự luận (Essay)",
)
async def submit_essay(
    request: EssaySubmissionRequest,
    current_user: AIUserDep,
    db: DbDep,
    use_case: EssayUseCase = Depends(get_essay_use_case),
):
    """
    Học sinh nộp bài văn tự luận.
    Bài sẽ được đưa vào queue (Celery) để AI chấm điểm.
    Trả về mã 202 Accepted.
    """
    try:
        submission, ai_task_id = await use_case.submit_essay(
            student=current_user,
            teacher_id=request.teacher_id,
            content=request.content,
            rubric_id=request.rubric_id
        )
        
        # Ngăn chặn Race Condition với Celery: Commit dữ liệu xuống DB trước khi bắn task
        await db.commit()
        
        use_case.dispatch_grading(submission.id, current_user.id, ai_task_id)
    except Exception as e:
        logger.error(f"Error submitting essay: {e}", exc_info=True)
        raise
    return ApiResponse(
        data=EssaySubmissionAcceptedResponse(
            submission_id=submission.id, ai_task_id=ai_task_id
        ),
        message="Đã nhận bài và đang tiến hành chấm điểm"
    )

@router.get(
    "/{submission_id}",
    response_model=ApiResponse[EssaySubmissionResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy kết quả bài tự luận",
)
async def get_essay_submission(
    submission_id: uuid.UUID,
    current_user: CurrentUserDep,
    use_case: EssayUseCase = Depends(get_essay_use_case),
):
    """
    Lấy thông tin bài tự luận cùng với điểm và phản hồi của AI.
    """
    submission = await use_case.get_essay(submission_id)
    if not submission:
        logger.warning(f"Submission not found: {submission_id}")
        raise NotFoundException("Bài nộp không tồn tại")
        
    # Security: Chỉ người nộp hoặc giáo viên liên quan mới được xem
    if current_user.role == "student" and submission.student_id != current_user.id:
        logger.warning(f"Student {current_user.id} tried to access submission {submission_id} belonging to {submission.student_id}")
        raise ForbiddenException("Bạn không có quyền xem bài này")
        
    return ApiResponse(data=submission)

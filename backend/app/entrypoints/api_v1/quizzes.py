import uuid

from fastapi import APIRouter, Depends, status

from app.core.dependencies import DbDep, CurrentUserDep
from app.core.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.domain.exceptions import (
    QuizNotFoundError,
    QuizAttemptNotFoundError,
    PermissionDeniedError,
    QuizAttemptAlreadySubmittedError,
)
import logging

logger = logging.getLogger(__name__)
from app.adapters.database.quiz_repository import SQLAlchemyQuizRepository
from app.adapters.database.quiz_attempt_repository import QuizAttemptRepository
from app.application.use_cases.quiz_use_case import QuizUseCase
from app.entrypoints.api_v1.schemas import ApiResponse
from app.entrypoints.api_v1.schemas.quiz import (
    QuizAttemptResponse,
    SubmitAttemptRequest,
)

router = APIRouter()

def get_quiz_use_case(db: DbDep) -> QuizUseCase:
    quiz_repo = SQLAlchemyQuizRepository(db)
    attempt_repo = QuizAttemptRepository(db)
    return QuizUseCase(quiz_repo=quiz_repo, attempt_repo=attempt_repo)

@router.post(
    "/{quiz_id}/attempts",
    response_model=ApiResponse[QuizAttemptResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Bắt đầu làm bài Quiz",
)
async def start_quiz_attempt(
    quiz_id: uuid.UUID,
    current_user: CurrentUserDep,
    use_case: QuizUseCase = Depends(get_quiz_use_case),
):
    """
    Học sinh bắt đầu làm bài.
    Hệ thống sẽ tạo ra một lượt làm bài mới (QuizAttempt) với started_at.
    """
    try:
        attempt = await use_case.start_attempt(quiz_id=quiz_id, student=current_user)
        return ApiResponse(data=attempt, message="Bắt đầu làm bài thành công")
    except QuizNotFoundError as e:
        logger.error(f"Quiz not found: {e}")
        raise NotFoundException(str(e))
    except Exception as e:
        logger.error(f"Unexpected error when starting quiz attempt: {e}", exc_info=True)
        raise

@router.post(
    "/{quiz_id}/attempts/{attempt_id}/submit",
    response_model=ApiResponse[QuizAttemptResponse],
    status_code=status.HTTP_200_OK,
    summary="Nộp bài Quiz",
)
async def submit_quiz_attempt(
    quiz_id: uuid.UUID,
    attempt_id: uuid.UUID,
    request: SubmitAttemptRequest,
    current_user: CurrentUserDep,
    use_case: QuizUseCase = Depends(get_quiz_use_case),
):
    """
    Học sinh nộp bài.
    Server tự động chấm điểm và lưu StudentAnswers.
    """
    try:
        attempt = await use_case.submit_attempt(
            attempt_id=attempt_id, student=current_user, answers=request.answers
        )
        return ApiResponse(data=attempt, message="Nộp bài thành công")
    except (QuizNotFoundError, QuizAttemptNotFoundError) as e:
        logger.error(f"Not found error in submit_quiz_attempt: {e}")
        raise NotFoundException(str(e))
    except QuizAttemptAlreadySubmittedError as e:
        logger.warning(f"Validation error in submit_quiz_attempt: {e}")
        raise ValidationException(str(e))
    except PermissionDeniedError as e:
        logger.warning(f"Forbidden error in submit_quiz_attempt: {e}")
        raise ForbiddenException(str(e))
    except Exception as e:
        logger.error(f"Unexpected error when submitting quiz attempt: {e}", exc_info=True)
        raise

@router.get(
    "/{quiz_id}/attempts",
    response_model=ApiResponse[list[QuizAttemptResponse]],
    status_code=status.HTTP_200_OK,
    summary="Lấy lịch sử làm bài Quiz",
)
async def list_quiz_attempts(
    quiz_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DbDep,
    cursor: uuid.UUID | None = None,
    limit: int = 10,
):
    """
    Xem lại lịch sử các lượt làm bài của chính học sinh.
    """
    attempt_repo = QuizAttemptRepository(db)
    attempts = await attempt_repo.get_by_student_and_quiz(
        student_id=current_user.id, quiz_id=quiz_id, cursor=cursor, limit=limit
    )
    return ApiResponse(data=attempts)

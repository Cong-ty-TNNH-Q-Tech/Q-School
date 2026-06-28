import uuid

from fastapi import APIRouter, Depends, status

from app.core.dependencies import DbDep, CurrentUserDep
from app.core.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.domain.exceptions import QuizNotFoundError, QuizAttemptNotFoundError, PermissionDeniedError
from app.adapters.database.quiz_repository import SQLAlchemyQuizRepository
from app.adapters.database.quiz_attempt_repository import QuizAttemptRepository
from app.application.use_cases.quiz_use_case import QuizUseCase
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
    response_model=QuizAttemptResponse,
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
        return await use_case.start_attempt(quiz_id=quiz_id, student=current_user)
    except QuizNotFoundError as e:
        raise NotFoundException(str(e))

@router.post(
    "/{quiz_id}/attempts/{attempt_id}/submit",
    response_model=QuizAttemptResponse,
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
        return await use_case.submit_attempt(
            attempt_id=attempt_id, student=current_user, answers=request.answers
        )
    except (QuizNotFoundError, QuizAttemptNotFoundError) as e:
        raise NotFoundException(str(e))
    except PermissionDeniedError as e:
        if "đã được nộp" in str(e):
            raise ValidationException(str(e))
        raise ForbiddenException(str(e))

@router.get(
    "/{quiz_id}/attempts",
    response_model=list[QuizAttemptResponse],
    status_code=status.HTTP_200_OK,
    summary="Lấy lịch sử làm bài Quiz",
)
async def list_quiz_attempts(
    quiz_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: DbDep,
):
    """
    Xem lại lịch sử các lượt làm bài của chính học sinh.
    """
    attempt_repo = QuizAttemptRepository(db)
    return await attempt_repo.get_by_student_and_quiz(
        student_id=current_user.id, quiz_id=quiz_id
    )

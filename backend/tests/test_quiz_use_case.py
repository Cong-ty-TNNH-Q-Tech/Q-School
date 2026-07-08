import pytest
import uuid
from unittest.mock import AsyncMock

from app.application.use_cases.quiz_use_case import QuizUseCase
from app.domain.models.quiz import QuizAttempt, Quiz, Question, Answer
from app.domain.models.user import User
from app.domain.exceptions import QuizNotFoundError, QuizAttemptNotFoundError, PermissionDeniedError

@pytest.fixture
def mock_quiz_repo():
    return AsyncMock()

@pytest.fixture
def mock_attempt_repo():
    return AsyncMock()

@pytest.fixture
def use_case(mock_quiz_repo, mock_attempt_repo):
    return QuizUseCase(quiz_repo=mock_quiz_repo, attempt_repo=mock_attempt_repo)

@pytest.mark.asyncio
async def test_start_attempt_success(use_case, mock_quiz_repo, mock_attempt_repo):
    student = User(id=uuid.uuid4(), role="student")
    quiz_id = uuid.uuid4()
    
    quiz = Quiz(id=quiz_id, title="Test Quiz")
    mock_quiz_repo.get_by_id.return_value = quiz
    
    expected_attempt = QuizAttempt(id=uuid.uuid4(), student_id=student.id, quiz_id=quiz_id)
    mock_attempt_repo.create.return_value = expected_attempt
    
    result = await use_case.start_attempt(quiz_id, student)
    
    assert result.id == expected_attempt.id
    mock_quiz_repo.get_by_id.assert_called_once_with(quiz_id)
    mock_attempt_repo.create.assert_called_once_with(student_id=student.id, quiz_id=quiz_id)

@pytest.mark.asyncio
async def test_start_attempt_not_found(use_case, mock_quiz_repo):
    student = User(id=uuid.uuid4(), role="student")
    quiz_id = uuid.uuid4()
    
    mock_quiz_repo.get_by_id.return_value = None
    
    with pytest.raises(QuizNotFoundError):
        await use_case.start_attempt(quiz_id, student)

@pytest.mark.asyncio
async def test_submit_attempt_success(use_case, mock_quiz_repo, mock_attempt_repo):
    student = User(id=uuid.uuid4(), role="student")
    quiz_id = uuid.uuid4()
    attempt_id = uuid.uuid4()
    
    q1_id = uuid.uuid4()
    ans1_id = uuid.uuid4()
    ans2_id = uuid.uuid4()
    
    quiz = Quiz(id=quiz_id, title="Test Quiz", questions=[
        Question(id=q1_id, question_text="Q1", answers=[
            Answer(id=ans1_id, is_correct=True),
            Answer(id=ans2_id, is_correct=False)
        ])
    ])
    
    attempt = QuizAttempt(id=attempt_id, student_id=student.id, quiz_id=quiz_id)
    
    mock_attempt_repo.get_by_id.return_value = attempt
    mock_quiz_repo.get_by_id.return_value = quiz
    mock_attempt_repo.complete.return_value = attempt # simplify
    
    answers = {q1_id: ans1_id}
    result = await use_case.submit_attempt(attempt_id, student, answers)
    
    assert mock_attempt_repo.complete.called
    args, _ = mock_attempt_repo.complete.call_args
    assert args[1] == 100.0 # score

@pytest.mark.asyncio
async def test_submit_attempt_forbidden(use_case, mock_attempt_repo):
    student = User(id=uuid.uuid4(), role="student")
    attempt = QuizAttempt(id=uuid.uuid4(), student_id=uuid.uuid4()) # different student
    
    mock_attempt_repo.get_by_id.return_value = attempt
    
    with pytest.raises(PermissionDeniedError):
        await use_case.submit_attempt(attempt.id, student, {})

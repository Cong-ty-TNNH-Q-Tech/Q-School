import pytest
import uuid
from unittest.mock import AsyncMock, Mock

from app.application.use_cases.essay_use_case import EssayUseCase
from app.domain.models.quiz import EssaySubmission
from app.domain.models.user import User

@pytest.fixture
def mock_essay_repo():
    return AsyncMock()

@pytest.fixture
def mock_ai_task_repo():
    return AsyncMock()

@pytest.fixture
def use_case(mock_essay_repo, mock_ai_task_repo):
    return EssayUseCase(essay_repo=mock_essay_repo, ai_task_repo=mock_ai_task_repo)

@pytest.mark.asyncio
async def test_submit_essay_success(use_case, mock_essay_repo, mock_ai_task_repo, monkeypatch):
    student = User(id=uuid.uuid4(), role="student")
    teacher_id = uuid.uuid4()
    rubric_id = uuid.uuid4()
    content = "This is a test essay"
    image_url = None
    
    mock_submission = EssaySubmission(id=uuid.uuid4(), student_id=student.id, teacher_id=teacher_id)
    mock_essay_repo.create.return_value = mock_submission
    
    mock_ai_task = Mock()
    mock_ai_task.id = uuid.uuid4()
    mock_ai_task_repo.create.return_value = mock_ai_task
    
    mock_apply_async = Mock()
    monkeypatch.setattr('app.entrypoints.celery_worker.ai_tasks.process_essay_grading.apply_async', mock_apply_async)
    
    result_submission, result_task_id = await use_case.submit_essay(student, teacher_id, content, rubric_id)
    
    assert result_submission == mock_submission
    assert result_task_id == mock_ai_task.id
    mock_essay_repo.create.assert_called_once_with(student_id=student.id, teacher_id=teacher_id, content=content, rubric_id=rubric_id)
    mock_ai_task_repo.create.assert_called_once_with(user_id=student.id, task_type="essay_grading")
    mock_apply_async.assert_called_once()

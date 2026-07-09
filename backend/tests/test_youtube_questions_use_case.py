import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.youtube_questions_use_case import GenerateVideoQuestionsUseCase

@pytest.fixture
def mock_youtube_adapter():
    return AsyncMock()

@pytest.fixture
def mock_llm_service():
    return AsyncMock()

@pytest.fixture
def use_case(mock_youtube_adapter, mock_llm_service):
    return GenerateVideoQuestionsUseCase(mock_youtube_adapter, mock_llm_service)

@pytest.mark.asyncio
async def test_execute_success(use_case, mock_youtube_adapter, mock_llm_service):
    # Setup
    mock_youtube_adapter.get_transcript.return_value = [
        {"start": 0, "duration": 5, "text": "Hello world"}
    ]
    mock_llm_service.generate.return_value = '''
    ```json
    [
      {
        "question_text": "What did they say?",
        "timestamp": 0,
        "answers": [
          {"text": "Hello world", "is_correct": true},
          {"text": "Goodbye", "is_correct": false},
          {"text": "Hi", "is_correct": false},
          {"text": "Bye", "is_correct": false}
        ]
      }
    ]
    ```
    '''
    
    # Act
    results = await use_case.execute("https://youtube.com/watch?v=12345678901", 1)
    
    # Assert
    assert len(results) == 1
    assert results[0]["question_text"] == "What did they say?"
    assert results[0]["timestamp"] == 0
    assert len(results[0]["answers"]) == 4

@pytest.mark.asyncio
async def test_execute_video_too_long(use_case, mock_youtube_adapter):
    mock_youtube_adapter.get_transcript.return_value = [
        {"start": 1801, "duration": 5, "text": "Too long"}
    ]
    
    with pytest.raises(ValueError, match="Video quá dài"):
        await use_case.execute("https://youtube.com/watch?v=12345678901", 5)

@pytest.mark.asyncio
async def test_execute_no_transcript(use_case, mock_youtube_adapter):
    mock_youtube_adapter.get_transcript.return_value = []
    
    with pytest.raises(ValueError, match="Video không có phụ đề"):
        await use_case.execute("https://youtube.com/watch?v=12345678901", 5)

@pytest.mark.asyncio
async def test_execute_invalid_url(use_case):
    with pytest.raises(ValueError, match="URL YouTube không hợp lệ"):
        await use_case.execute("https://invalid.com/video", 5)

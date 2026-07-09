import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.adapters.youtube_transcript_adapter import YouTubeTranscriptAdapter
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound

@pytest.fixture
def adapter():
    return YouTubeTranscriptAdapter()

@pytest.mark.asyncio
@patch('app.adapters.youtube_transcript_adapter.YouTubeTranscriptApi.get_transcript')
async def test_get_transcript_success(mock_get_transcript, adapter):
    mock_get_transcript.return_value = [
        {"start": 0, "duration": 5, "text": "Hello"}
    ]
    
    result = await adapter.get_transcript("12345678901")
    assert len(result) == 1
    assert result[0]["text"] == "Hello"

@pytest.mark.asyncio
@patch('app.adapters.youtube_transcript_adapter.YouTubeTranscriptApi.get_transcript')
@patch('app.adapters.youtube_transcript_adapter.YouTubeTranscriptAdapter._fallback_transcribe')
async def test_get_transcript_fallback(mock_fallback, mock_get_transcript, adapter):
    mock_get_transcript.side_effect = TranscriptsDisabled("12345678901")
    mock_fallback.return_value = [{"start": 0, "duration": 5, "text": "Fallback text"}]
    
    result = await adapter.get_transcript("12345678901")
    assert len(result) == 1
    assert result[0]["text"] == "Fallback text"
    mock_fallback.assert_called_once_with("12345678901")

@pytest.mark.asyncio
@patch('app.adapters.youtube_transcript_adapter.YouTubeTranscriptApi.get_transcript')
async def test_get_transcript_other_exception(mock_get_transcript, adapter):
    mock_get_transcript.side_effect = Exception("Some network error")
    
    with pytest.raises(ValueError, match="Không thể tải phụ đề"):
        await adapter.get_transcript("12345678901")

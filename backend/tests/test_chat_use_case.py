import uuid
from datetime import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.use_cases.chat_use_case import ChatUseCase
from app.application.ports.outbound.ai_repository import IChatRepository
from app.application.ports.outbound.llm_service import ILLMService
from app.domain.models.ai import ChatSession, ChatMessage
from app.domain.models.user import User


@pytest.fixture
def chat_repo_mock():
    return AsyncMock(spec=IChatRepository)


@pytest.fixture
def llm_service_mock():
    llm = MagicMock(spec=ILLMService)

    async def mock_stream(*args, **kwargs):
        for token in ["Hello", " ", "World"]:
            yield token

    llm.stream_chat = mock_stream
    return llm


@pytest.fixture
def use_case(chat_repo_mock, llm_service_mock):
    return ChatUseCase(chat_repo_mock, llm_service_mock)


@pytest.mark.asyncio
async def test_create_session(use_case, chat_repo_mock):
    user = User(id=uuid.uuid4(), username="test_user")
    expected_session = ChatSession(id=uuid.uuid4(), user_id=user.id, title="Test", ai_persona="assistant")
    chat_repo_mock.create_session.return_value = expected_session

    session = await use_case.create_session(user, title="Test", ai_persona="assistant")
    
    assert session == expected_session
    chat_repo_mock.create_session.assert_called_once_with(user_id=user.id, title="Test", ai_persona="assistant")


@pytest.mark.asyncio
async def test_send_message_stream_and_save(use_case, chat_repo_mock, llm_service_mock):
    session = ChatSession(id=uuid.uuid4(), user_id=uuid.uuid4(), ai_persona="You are a helpful assistant")
    user = User(id=session.user_id, username="test_user")
    
    chat_repo_mock.get_session_by_id.return_value = session
    
    # Mock history messages
    history_msg = ChatMessage(id=uuid.uuid4(), session_id=session.id, sender_type="user", content="Hi")
    chat_repo_mock.get_messages.return_value = [history_msg]

    stream_generator = await use_case.send_message(session.id, user, "How are you?")
    
    # Act
    tokens = []
    async for token in stream_generator:
        tokens.append(token)

    # Assert
    assert tokens == ["Hello", " ", "World"]
    
    # Ensure add_message was called for user
    chat_repo_mock.add_message.assert_any_call(session_id=session.id, sender_type="user", content="How are you?")
    
    # Ensure add_message was called for AI after stream finished
    chat_repo_mock.add_message.assert_any_call(session_id=session.id, sender_type="ai", content="Hello World")

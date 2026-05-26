"""
Test suite cho VLLMAdapter — LLM Service Adapter.
Dung httpx mock va unittest.mock de test khong can vLLM server that.

Test Strategy:
  - Mock openai.AsyncOpenAI client
  - Test stream_chat: verify async iterator output
  - Test generate: verify non-streaming output
  - Test embed: verify dimension validation
  - Test error handling: connection, timeout, rate limit
  - Test factory: verify provider selection
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from collections.abc import AsyncIterator

from app.adapters.llm_client.vllm_adapter import (
    VLLMAdapter,
    LLMConnectionError,
    LLMRateLimitError,
    EmbeddingDimensionError,
    LLMAdapterError,
)
from app.application.ports.outbound.llm_service import EMBEDDING_DIMENSION


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────
@pytest.fixture
def adapter():
    """VLLMAdapter voi test config (khong ket noi that)."""
    return VLLMAdapter(
        api_url="http://test-vllm:8001/v1",
        api_key="test_key",
        generation_model="test-model",
        embedding_api_url="http://test-embed:8001/v1",
        embedding_model="test-embed-model",
        timeout=10.0,
        max_retries=1,
    )


# ──────────────────────────────────────────────
# Helper: Mock stream response
# ──────────────────────────────────────────────
class MockStreamChunk:
    """Mock OpenAI streaming chunk."""
    def __init__(self, content: str | None):
        self.choices = [MagicMock(delta=MagicMock(content=content))]


class MockEmptyChunk:
    """Mock chunk voi empty choices."""
    def __init__(self):
        self.choices = []


async def _mock_stream_response(chunks: list[str]):
    """Create async iterator of mock chunks."""
    for content in chunks:
        yield MockStreamChunk(content)


# ──────────────────────────────────────────────
# Test: stream_chat
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_stream_chat_success(adapter: VLLMAdapter):
    """stream_chat tra ve tung token tu LLM."""
    mock_chunks = ["Hello", " ", "World", "!"]

    with patch.object(
        adapter._gen_client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=_mock_stream_response(mock_chunks),
    ):
        tokens = []
        async for token in adapter.stream_chat(
            messages=[{"role": "user", "content": "Hi"}]
        ):
            tokens.append(token)

        assert tokens == ["Hello", " ", "World", "!"]


@pytest.mark.asyncio
async def test_stream_chat_empty_response(adapter: VLLMAdapter):
    """stream_chat voi response rong tra ve iterator rong."""
    async def empty_stream():
        return
        yield  # noqa: unreachable — make this an async generator

    with patch.object(
        adapter._gen_client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=empty_stream(),
    ):
        tokens = []
        async for token in adapter.stream_chat(
            messages=[{"role": "user", "content": "Hi"}]
        ):
            tokens.append(token)

        assert tokens == []


@pytest.mark.asyncio
async def test_stream_chat_custom_model(adapter: VLLMAdapter):
    """stream_chat cho phep override model."""
    with patch.object(
        adapter._gen_client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=_mock_stream_response(["OK"]),
    ) as mock_create:
        async for _ in adapter.stream_chat(
            messages=[{"role": "user", "content": "Hi"}],
            model="custom-model",
        ):
            pass

        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args
        assert call_kwargs.kwargs.get("model") == "custom-model" or call_kwargs[1].get("model") == "custom-model"


@pytest.mark.asyncio
async def test_stream_chat_connection_error(adapter: VLLMAdapter):
    """stream_chat raise LLMConnectionError khi server khong phan hoi."""
    from openai import APIConnectionError

    with patch.object(
        adapter._gen_client.chat.completions,
        "create",
        side_effect=APIConnectionError(request=MagicMock()),
    ):
        with pytest.raises(LLMConnectionError):
            async for _ in adapter.stream_chat(
                messages=[{"role": "user", "content": "Hi"}]
            ):
                pass


@pytest.mark.asyncio
async def test_stream_chat_rate_limit(adapter: VLLMAdapter):
    """stream_chat raise LLMRateLimitError khi 429."""
    from openai import RateLimitError

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {}

    with patch.object(
        adapter._gen_client.chat.completions,
        "create",
        side_effect=RateLimitError(
            message="Rate limited",
            response=mock_response,
            body=None,
        ),
    ):
        with pytest.raises(LLMRateLimitError):
            async for _ in adapter.stream_chat(
                messages=[{"role": "user", "content": "Hi"}]
            ):
                pass


# ──────────────────────────────────────────────
# Test: generate
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_generate_success(adapter: VLLMAdapter):
    """generate tra ve full text response."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Generated lesson plan content"))
    ]

    with patch.object(
        adapter._gen_client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await adapter.generate("Create a lesson plan about Python")
        assert result == "Generated lesson plan content"


@pytest.mark.asyncio
async def test_generate_empty_choices(adapter: VLLMAdapter):
    """generate tra ve empty string khi khong co choices."""
    mock_response = MagicMock()
    mock_response.choices = []

    with patch.object(
        adapter._gen_client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await adapter.generate("Test prompt")
        assert result == ""


@pytest.mark.asyncio
async def test_generate_none_content(adapter: VLLMAdapter):
    """generate tra ve empty string khi content=None."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=None))]

    with patch.object(
        adapter._gen_client.chat.completions,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await adapter.generate("Test prompt")
        assert result == ""


@pytest.mark.asyncio
async def test_generate_connection_error(adapter: VLLMAdapter):
    """generate raise LLMConnectionError khi server down."""
    from openai import APIConnectionError

    with patch.object(
        adapter._gen_client.chat.completions,
        "create",
        new_callable=AsyncMock,
        side_effect=APIConnectionError(request=MagicMock()),
    ):
        with pytest.raises(LLMConnectionError):
            await adapter.generate("Test prompt")


# ──────────────────────────────────────────────
# Test: embed
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_embed_success(adapter: VLLMAdapter):
    """embed tra ve vector dung dimension."""
    fake_embedding = [0.1] * EMBEDDING_DIMENSION

    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=fake_embedding)]

    with patch.object(
        adapter._embed_client.embeddings,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        result = await adapter.embed("Hello world")
        assert len(result) == EMBEDDING_DIMENSION
        assert result == fake_embedding


@pytest.mark.asyncio
async def test_embed_wrong_dimension(adapter: VLLMAdapter):
    """embed raise EmbeddingDimensionError khi dimension sai."""
    wrong_embedding = [0.1] * 768  # Wrong dimension

    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=wrong_embedding)]

    with patch.object(
        adapter._embed_client.embeddings,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        with pytest.raises(EmbeddingDimensionError, match="expected 1536, got 768"):
            await adapter.embed("Hello world")


@pytest.mark.asyncio
async def test_embed_empty_response(adapter: VLLMAdapter):
    """embed raise LLMAdapterError khi response rong."""
    mock_response = MagicMock()
    mock_response.data = []

    with patch.object(
        adapter._embed_client.embeddings,
        "create",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        with pytest.raises(LLMAdapterError, match="data rong"):
            await adapter.embed("Hello world")


@pytest.mark.asyncio
async def test_embed_connection_error(adapter: VLLMAdapter):
    """embed raise LLMConnectionError khi embedding server down."""
    from openai import APIConnectionError

    with patch.object(
        adapter._embed_client.embeddings,
        "create",
        new_callable=AsyncMock,
        side_effect=APIConnectionError(request=MagicMock()),
    ):
        with pytest.raises(LLMConnectionError):
            await adapter.embed("Hello world")


@pytest.mark.asyncio
async def test_embed_rate_limit(adapter: VLLMAdapter):
    """embed raise LLMRateLimitError khi embedding server 429."""
    from openai import RateLimitError

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {}

    with patch.object(
        adapter._embed_client.embeddings,
        "create",
        new_callable=AsyncMock,
        side_effect=RateLimitError(
            message="Rate limited",
            response=mock_response,
            body=None,
        ),
    ):
        with pytest.raises(LLMRateLimitError):
            await adapter.embed("Hello world")


# ──────────────────────────────────────────────
# Test: Factory
# ──────────────────────────────────────────────
def test_factory_creates_vllm_adapter():
    """Factory tao VLLMAdapter khi provider=vllm."""
    from app.adapters.llm_client.llm_factory import create_llm_service
    from app.application.ports.outbound.llm_service import ILLMService

    service = create_llm_service(provider="vllm")
    assert isinstance(service, ILLMService)
    assert isinstance(service, VLLMAdapter)


def test_factory_creates_openai_adapter():
    """Factory tao VLLMAdapter khi provider=openai (cung OpenAI-compatible)."""
    from app.adapters.llm_client.llm_factory import create_llm_service

    service = create_llm_service(provider="openai")
    assert isinstance(service, VLLMAdapter)


def test_factory_default_provider():
    """Factory mac dinh dung vllm provider."""
    from app.adapters.llm_client.llm_factory import create_llm_service

    service = create_llm_service()
    assert isinstance(service, VLLMAdapter)


def test_factory_unsupported_provider():
    """Factory raise ValueError cho provider khong hop le."""
    from app.adapters.llm_client.llm_factory import create_llm_service

    with pytest.raises(ValueError, match="khong duoc support"):
        create_llm_service(provider="gemini")


# ──────────────────────────────────────────────
# Test: Adapter close
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_adapter_close(adapter: VLLMAdapter):
    """close() dong cac HTTP clients."""
    with patch.object(adapter._gen_client, "close", new_callable=AsyncMock) as mock_gen_close:
        with patch.object(adapter._embed_client, "close", new_callable=AsyncMock) as mock_embed_close:
            await adapter.close()
            mock_gen_close.assert_called_once()
            mock_embed_close.assert_called_once()

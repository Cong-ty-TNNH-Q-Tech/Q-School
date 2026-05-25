"""
VLLMAdapter — Concrete implementation cua ILLMService.
Ket noi voi vLLM server hoac OpenAI API thong qua OpenAI-compatible interface.

Hexagonal Architecture:
  - Day la DRIVEN ADAPTER (Secondary) — implement outbound port ILLMService
  - Use Cases inject ILLMService, KHONG biet adapter cu the
  - Config doc tu Settings (VLLM_API_URL, VLLM_API_KEY, VLLM_MODEL_NAME...)

Design Decisions:
  - Dung openai SDK (OpenAI-compatible) thay vi raw httpx de:
    + Tu dong handle SSE parsing, retries, error mapping
    + vLLM, LMStudio, Ollama deu support OpenAI-compatible API
  - stream_chat: AsyncIterator[str] cho SSE streaming (AGENTS.md mandate)
  - generate: non-streaming cho Celery background tasks
  - embed: Dung EMBEDDING model rieng (KHAC generation model)
  - Retry logic: tenacity voi exponential backoff

Luu y AGENTS.md:
  - KHONG hardcode API keys — doc tu Settings (environment variables)
  - KHONG import FastAPI, SQLAlchemy, HTTP exceptions o day
  - Day la adapter thuan tuy, chi giao tiep voi external LLM service
"""
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx
from openai import AsyncOpenAI, APIConnectionError, APITimeoutError, RateLimitError

from app.application.ports.outbound.llm_service import ILLMService, EMBEDDING_DIMENSION
from app.core.config import settings

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Retry constants
# ──────────────────────────────────────────────
MAX_RETRIES = 3
TIMEOUT_SECONDS = 120  # vLLM co the cham voi long context


class LLMAdapterError(Exception):
    """Base exception cho LLM adapter failures."""
    pass


class LLMConnectionError(LLMAdapterError):
    """vLLM server khong phan hoi hoac timeout."""
    pass


class LLMRateLimitError(LLMAdapterError):
    """vLLM server tra ve 429 Too Many Requests."""
    pass


class EmbeddingDimensionError(LLMAdapterError):
    """Embedding output dimension khong match EMBEDDING_DIMENSION."""
    pass


class VLLMAdapter(ILLMService):
    """
    Concrete Adapter: Ket noi voi vLLM/OpenAI-compatible server.

    Phan biet 2 loai model:
      - GENERATION (Qwen2.5-7B-Instruct): stream_chat(), generate()
      - EMBEDDING (Qwen2.5-Embedding-1.5B): embed()

    Moi loai co the chay tren endpoint rieng (VLLM_API_URL vs EMBEDDING_API_URL).
    """

    def __init__(
        self,
        *,
        api_url: str | None = None,
        api_key: str | None = None,
        generation_model: str | None = None,
        embedding_api_url: str | None = None,
        embedding_model: str | None = None,
        timeout: float = TIMEOUT_SECONDS,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        """
        Init adapter voi config tu Settings hoac override params.

        Args:
            api_url: Base URL cho generation model (default: settings.VLLM_API_URL)
            api_key: API key (default: settings.VLLM_API_KEY)
            generation_model: Model name cho chat/generate (default: settings.VLLM_MODEL_NAME)
            embedding_api_url: Base URL cho embedding model (default: settings.EMBEDDING_API_URL)
            embedding_model: Model name cho embedding (default: settings.EMBEDDING_MODEL_NAME)
            timeout: Request timeout in seconds
            max_retries: So lan retry khi connection error
        """
        self._api_url = api_url or settings.VLLM_API_URL
        self._api_key = api_key or settings.VLLM_API_KEY
        self._generation_model = generation_model or settings.VLLM_MODEL_NAME
        self._embedding_api_url = embedding_api_url or settings.EMBEDDING_API_URL
        self._embedding_model = embedding_model or settings.EMBEDDING_MODEL_NAME
        self._timeout = timeout
        self._max_retries = max_retries

        # OpenAI client cho GENERATION (stream_chat, generate)
        self._gen_client = AsyncOpenAI(
            base_url=self._api_url,
            api_key=self._api_key,
            timeout=httpx.Timeout(self._timeout, connect=10.0),
            max_retries=self._max_retries,
        )

        # OpenAI client cho EMBEDDING (co the endpoint rieng)
        # Neu EMBEDDING_API_URL == VLLM_API_URL, dung chung client cung duoc
        # nhung tach rieng de linh hoat deploy
        self._embed_client = AsyncOpenAI(
            base_url=self._embedding_api_url,
            api_key=self._api_key,
            timeout=httpx.Timeout(self._timeout, connect=10.0),
            max_retries=self._max_retries,
        )

        logger.info(
            "VLLMAdapter initialized: gen=%s@%s, embed=%s@%s",
            self._generation_model, self._api_url,
            self._embedding_model, self._embedding_api_url,
        )

    # ──────────────────────────────────────────────
    # stream_chat: AsyncIterator[str] cho SSE
    # ──────────────────────────────────────────────
    async def stream_chat(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """
        Stream phan hoi AI tung token qua OpenAI-compatible streaming.
        Output: AsyncIterator[str] — moi item la mot text chunk.

        Usage trong Router:
            async def sse_endpoint():
                async for token in llm.stream_chat(messages):
                    yield f"data: {token}\\n\\n"

        Raises:
            LLMConnectionError: vLLM server khong phan hoi
            LLMRateLimitError: 429 Too Many Requests
        """
        resolved_model = model or self._generation_model

        try:
            stream = await self._gen_client.chat.completions.create(
                model=resolved_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except APIConnectionError as e:
            logger.error("LLM connection failed: %s", e)
            raise LLMConnectionError(
                f"Khong the ket noi den LLM server tai {self._api_url}: {e}"
            ) from e
        except APITimeoutError as e:
            logger.error("LLM request timeout: %s", e)
            raise LLMConnectionError(
                f"LLM server timeout sau {self._timeout}s: {e}"
            ) from e
        except RateLimitError as e:
            logger.warning("LLM rate limited: %s", e)
            raise LLMRateLimitError(
                f"LLM server rate limit (429): {e}"
            ) from e

    # ──────────────────────────────────────────────
    # generate: non-streaming cho background tasks
    # ──────────────────────────────────────────────
    async def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """
        Generate text (non-streaming) cho Celery background tasks.
        Dung khi khong can real-time: sinh giao an, cham bai tu luan.

        Converts prompt string sang messages format [{role: "user", content: prompt}].

        Returns:
            str: Full generated text.

        Raises:
            LLMConnectionError: vLLM server khong phan hoi
            LLMRateLimitError: 429 Too Many Requests
            LLMAdapterError: Unexpected error
        """
        resolved_model = model or self._generation_model
        messages = [{"role": "user", "content": prompt}]

        try:
            response = await self._gen_client.chat.completions.create(
                model=resolved_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )

            if not response.choices:
                logger.warning("LLM returned empty choices for prompt: %s...", prompt[:100])
                return ""

            return response.choices[0].message.content or ""

        except APIConnectionError as e:
            logger.error("LLM connection failed: %s", e)
            raise LLMConnectionError(
                f"Khong the ket noi den LLM server tai {self._api_url}: {e}"
            ) from e
        except APITimeoutError as e:
            logger.error("LLM request timeout: %s", e)
            raise LLMConnectionError(
                f"LLM server timeout sau {self._timeout}s: {e}"
            ) from e
        except RateLimitError as e:
            logger.warning("LLM rate limited: %s", e)
            raise LLMRateLimitError(
                f"LLM server rate limit (429): {e}"
            ) from e

    # ──────────────────────────────────────────────
    # embed: Vector embedding cho RAG
    # ──────────────────────────────────────────────
    async def embed(self, text: str) -> list[float]:
        """
        Tao vector embedding cho RAG (DocumentChunk).

        Su dung EMBEDDING model (KHAC generation model):
          - Generation: Qwen2.5-7B-Instruct (chat/generate)
          - Embedding: Qwen2.5-Embedding-1.5B (embed)

        Output PHAI co dung EMBEDDING_DIMENSION chieu (default 1536).
        Neu dimension khong match, raise EmbeddingDimensionError de fail fast
        thay vi de PostgreSQL reject insert (kho debug hon).

        Returns:
            list[float]: Vector embedding voi dung EMBEDDING_DIMENSION chieu.

        Raises:
            EmbeddingDimensionError: Output dimension khong match
            LLMConnectionError: Embedding server khong phan hoi
        """
        try:
            response = await self._embed_client.embeddings.create(
                model=self._embedding_model,
                input=text,
            )

            if not response.data:
                raise LLMAdapterError("Embedding response tra ve data rong")

            embedding = response.data[0].embedding
            actual_dim = len(embedding)

            if actual_dim != EMBEDDING_DIMENSION:
                raise EmbeddingDimensionError(
                    f"Embedding dimension mismatch: "
                    f"expected {EMBEDDING_DIMENSION}, got {actual_dim}. "
                    f"Model '{self._embedding_model}' tra ve sai dimension. "
                    f"Kiem tra EMBEDDING_MODEL_NAME trong .env hoac "
                    f"cap nhat Vector({actual_dim}) trong DocumentChunk migration."
                )

            return embedding

        except APIConnectionError as e:
            logger.error("Embedding connection failed: %s", e)
            raise LLMConnectionError(
                f"Khong the ket noi den Embedding server tai {self._embedding_api_url}: {e}"
            ) from e
        except APITimeoutError as e:
            logger.error("Embedding request timeout: %s", e)
            raise LLMConnectionError(
                f"Embedding server timeout sau {self._timeout}s: {e}"
            ) from e

    # ──────────────────────────────────────────────
    # Lifecycle
    # ──────────────────────────────────────────────
    async def close(self) -> None:
        """Cleanup: Dong HTTP clients."""
        await self._gen_client.close()
        await self._embed_client.close()
        logger.info("VLLMAdapter closed")

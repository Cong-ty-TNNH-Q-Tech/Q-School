"""
Outbound Port — AI Inference Service Interface.
Use Case gọi interface này để tương tác với vLLM/OpenAI — không biết provider cụ thể.
Adapter thực tế ở: adapters/llm_client/vllm_adapter.py
"""
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class ILLMService(ABC):
    """
    Abstract Port: Contract cho AI Inference (vLLM, OpenAI, Claude...).
    Stream-first: mọi phương thức đều trả về AsyncIterator[str] cho SSE.
    """

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """
        Stream phản hồi AI từng token.
        Output: AsyncIterator[str] — mỗi item là một token/chunk text.
        Caller dùng 'async for token in stream_chat(...)'.
        """
        ...

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """
        Generate text (non-streaming) cho background tasks (Celery).
        Dùng khi không cần real-time streaming (sinh giáo án, chấm bài).
        """
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """
        Tạo vector embedding cho RAG (DocumentChunk).
        Output: list[float] với dimension phù hợp với Vector(1536) trong DB.
        """
        ...

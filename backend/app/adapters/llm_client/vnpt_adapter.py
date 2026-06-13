"""
VNPTAdapter — Concrete implementation của ILLMService.
Kết nối với các API của VNPT (đặc biệt là VNPT Smartbot) thay cho vLLM.

Tạm thời cấu trúc các hàm bám sát interface ILLMService hiện tại
nhưng sẽ tùy chỉnh logic gọi HTTP request cho phù hợp với tài liệu API của VNPT.
"""
import logging
from collections.abc import AsyncIterator

import httpx

from app.application.ports.outbound.llm_service import ILLMService, EMBEDDING_DIMENSION
from app.core.config import settings

logger = logging.getLogger(__name__)

class VNPTAdapterError(Exception):
    """Base exception cho VNPT adapter failures."""
    pass

class VNPTConnectionError(VNPTAdapterError):
    pass

class VNPTAdapter(ILLMService):
    """
    Concrete Adapter: Kết nối với VNPT API (Smartbot / SmartReader).
    Được tạo ra để đáp ứng yêu cầu chuyển đổi sang dùng API nội địa,
    tuân thủ Nghị định 13/2023/NĐ-CP theo yêu cầu của dự án.
    """

    def __init__(
        self,
        *,
        api_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        # Tạm thời đọc từ config hoặc truyền trực tiếp
        # Bạn sẽ cần bổ sung các biến môi trường VNPT_API_URL, VNPT_API_KEY vào file .env
        self._api_url = api_url or getattr(settings, "VNPT_API_URL", "https://api.vnpt.vn/smartbot")
        self._api_key = api_key or getattr(settings, "VNPT_API_KEY", "")
        self._timeout = timeout

        self._client = httpx.AsyncClient(
            base_url=self._api_url,
            timeout=httpx.Timeout(self._timeout),
            headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        )

        logger.info("VNPTAdapter initialized with URL: %s", self._api_url)

    async def stream_chat(
        self,
        messages: list[dict],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """
        Giao tiếp với VNPT Smartbot dạng streaming.
        Cần điều chỉnh parser tùy thuộc vào cấu trúc trả về thực tế của VNPT API.
        """
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if model:
            payload["model"] = model

        try:
            async with self._client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    # Parse chunk dựa trên spec của VNPT (Tạm thời yield thô)
                    if chunk:
                        yield chunk
        except httpx.RequestError as e:
            logger.error("VNPT Smartbot connection failed: %s", e)
            raise VNPTConnectionError(f"Lỗi kết nối VNPT: {e}") from e

    async def generate(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """
        Gọi API non-streaming cho các tác vụ như sinh giáo án, chấm bài văn.
        """
        payload = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if model:
            payload["model"] = model

        try:
            response = await self._client.post("/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            # Cần chỉnh key trả về theo đúng chuẩn API của VNPT
            return data.get("text", "")
        except httpx.RequestError as e:
            logger.error("VNPT Smartbot generate failed: %s", e)
            raise VNPTConnectionError(f"Lỗi gọi VNPT API: {e}") from e

    async def embed(self, text: str) -> list[float]:
        """
        Tạo vector embedding. Nếu VNPT không hỗ trợ model embedding chuẩn 1536 chiều,
        có thể sẽ cần cấu hình lại CSDL PostgreSQL (pgvector).
        """
        try:
            response = await self._client.post("/embeddings", json={"input": text})
            response.raise_for_status()
            data = response.json()
            # Mapping tùy theo data structure của VNPT
            embedding = data.get("data", [{}])[0].get("embedding", [])
            return embedding
        except httpx.RequestError as e:
            logger.error("VNPT Smartbot embedding failed: %s", e)
            raise VNPTConnectionError(f"Lỗi tạo embedding VNPT: {e}") from e

    async def close(self) -> None:
        await self._client.aclose()
        logger.info("VNPTAdapter closed")

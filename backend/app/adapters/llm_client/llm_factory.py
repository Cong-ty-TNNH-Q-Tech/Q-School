"""
LLM Factory — Factory Pattern de khoi tao LLM Adapter theo config.

AGENTS.md Design Pattern mandate:
  - Factory Pattern: Su dung de khoi tao cac Adapter phuc tap
    (VD: Khoi tao Client goi den vLLM hay OpenAI tuy theo cau hinh moi truong).
  - Open/Closed Principle: Khi them provider moi (Claude, Gemini),
    tao class moi ke thua ILLMService, KHONG sua code cu.

Usage:
    from app.adapters.llm_client.llm_factory import create_llm_service
    llm = create_llm_service()  # Doc settings tu .env
"""
import logging

from app.application.ports.outbound.llm_service import ILLMService
from app.core.config import settings

logger = logging.getLogger(__name__)

# Singleton instance — lazily initialized
_llm_instance: ILLMService | None = None


def create_llm_service(
    *,
    provider: str | None = None,
    **kwargs,
) -> ILLMService:
    """
    Factory: Khoi tao ILLMService implementation dua tren config.

    Hien tai chi support VLLMAdapter (OpenAI-compatible).
    Khi can them provider khac (Claude, Gemini), them elif o day.

    Args:
        provider: Override provider type. Neu None, mac dinh "vllm".
        **kwargs: Forward den adapter constructor.

    Returns:
        ILLMService: Concrete adapter instance.

    Raises:
        ValueError: Provider khong duoc support.
    """
    resolved_provider = (provider or "vllm").lower()

    if resolved_provider in ("vllm", "openai"):
        from app.adapters.llm_client.vllm_adapter import VLLMAdapter
        logger.info("Creating VLLMAdapter (provider=%s)", resolved_provider)
        return VLLMAdapter(**kwargs)

    raise ValueError(
        f"LLM provider '{resolved_provider}' khong duoc support. "
        f"Supported: vllm, openai"
    )


def get_llm_service() -> ILLMService:
    """
    Singleton getter: Tra ve LLM service instance duy nhat.
    Khoi tao lan dau khi goi, reuse cho cac lan sau.

    Usage trong FastAPI Depends:
        def get_llm(llm: ILLMService = Depends(get_llm_service)):
            ...
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = create_llm_service()
    return _llm_instance

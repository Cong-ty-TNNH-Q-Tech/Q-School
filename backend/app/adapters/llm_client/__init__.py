"""
LLM Client Adapter Package.
Provides concrete ILLMService implementations for vLLM/OpenAI-compatible servers.

Public API:
  - VLLMAdapter: Concrete adapter (driven adapter)
  - create_llm_service: Factory function
  - get_llm_service: Singleton getter for FastAPI Depends
  - Error types: LLMAdapterError, LLMConnectionError, LLMRateLimitError, EmbeddingDimensionError
"""
from app.adapters.llm_client.vllm_adapter import (  # noqa: F401
    VLLMAdapter,
    LLMAdapterError,
    LLMConnectionError,
    LLMRateLimitError,
    EmbeddingDimensionError,
)
from app.adapters.llm_client.llm_factory import (  # noqa: F401
    create_llm_service,
    get_llm_service,
)

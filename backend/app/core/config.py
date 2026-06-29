"""
Core Configuration — Load tất cả biến môi trường từ .env bằng pydantic-settings.
Không hardcode bất kỳ giá trị nhạy cảm nào tại đây.
"""

from functools import lru_cache
from typing import List
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ──────────────────────────────────────────────
    # App
    # ──────────────────────────────────────────────
    APP_NAME: str = "Q-School AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    APP_ENV: str = "development"  # development | staging | production

    # ──────────────────────────────────────────────
    # CORS
    # ──────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ──────────────────────────────────────────────
    # Database (PostgreSQL)
    # ──────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/qschool"

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """URL đồng bộ cho Alembic migration (dùng psycopg2)."""
        url = self.DATABASE_URL
        if "+asyncpg" in url:
            return url.replace("+asyncpg", "+psycopg2")
        if "+aiosqlite" in url:
            return url.replace("+aiosqlite", "")
        # Fallback: giả định đã là sync URL
        return url

    # ──────────────────────────────────────────────
    # Redis & Celery
    # ──────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"  # App sử dụng (future: rate limiting)
    CELERY_BROKER_URL: str = (
        "redis://localhost:6379/1"  # Celery task queue (DB 1, tách biệt)
    )
    CELERY_RESULT_BACKEND: str = (
        "redis://localhost:6379/2"  # Celery results (DB 2, tách biệt)
    )

    # ──────────────────────────────────────────────
    # JWT Security
    # ──────────────────────────────────────────────
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_OPENSSL_RAND_HEX_32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ──────────────────────────────────────────────
    # vLLM / AI Inference
    # ──────────────────────────────────────────────
    VLLM_API_URL: str = "http://localhost:8001/v1"
    VLLM_API_KEY: str = "dev_key_only"
    VLLM_MODEL_NAME: str = "Qwen/Qwen2.5-7B-Instruct"  # Generation model

    # Embedding model (KHÁC với generation model — dùng cho RAG).
    # Phải match với EMBEDDING_DIMENSION trong llm_service.py (default 1536).
    # Ví dụ: "Qwen/Qwen2.5-Embedding-1.5B" hoặc "text-embedding-ada-002"
    EMBEDDING_MODEL_NAME: str = "Qwen/Qwen2.5-Embedding-1.5B"
    EMBEDDING_API_URL: str = "http://localhost:8001/v1"  # Có thể là endpoint riêng

    # ──────────────────────────────────────────────
    # Object Storage (Cloudflare R2 / MinIO / S3)
    # ──────────────────────────────────────────────
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "qschool-uploads"
    S3_PUBLIC_URL: str = "http://localhost:9000/qschool-uploads"

    # ──────────────────────────────────────────────
    # Rate Limiting (SaaS)
    # ──────────────────────────────────────────────
    FREE_PLAN_AI_REQUESTS_PER_DAY: int = 10
    PRO_PLAN_AI_REQUESTS_PER_DAY: int = 200

    # ──────────────────────────────────────────────
    # Payment (SePay)
    # ──────────────────────────────────────────────
    SEPAY_API_TOKEN: str = "test_api_token"
    SEPAY_WEBHOOK_SECRET: str = "test_webhook_secret"
    SEPAY_ACCOUNT_NUMBER: str = "0010000000355"
    SEPAY_BANK: str = "Vietcombank"

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """
        Guard: Ngăn deploy production/staging với SECRET_KEY mặc định.

        - APP_ENV='production': Bắt buộc phải có SECRET_KEY hợp lệ.
        - APP_ENV='staging': Cũng bắt buộc — staging cần được bảo mật như production.
        - APP_ENV='development' và DEBUG=True: Bỏ qua (cho phép dùng key mặc định local).

        Ủu tiên kiểm tra APP_ENV trước (rõ ràng hơn DEBUG flag).
        """
        _DEFAULT_KEY = "CHANGE_ME_IN_PRODUCTION_USE_OPENSSL_RAND_HEX_32"
        is_prod_or_staging = self.APP_ENV in ("production", "staging")

        if is_prod_or_staging and self.SECRET_KEY == _DEFAULT_KEY:
            raise ValueError(
                f"SECRET_KEY is still the default value in APP_ENV='{self.APP_ENV}'! "
                "Run: openssl rand -hex 32  and set SECRET_KEY in .env"
            )

        # Fallback: Nếu DEBUG=False nhưng APP_ENV chưa set — vẫn guard
        if (
            not self.DEBUG
            and self.APP_ENV == "development"
            and self.SECRET_KEY == _DEFAULT_KEY
        ):
            import warnings

            warnings.warn(
                "Running with DEBUG=False and default SECRET_KEY. "
                "Set APP_ENV=production or use a real SECRET_KEY.",
                stacklevel=2,
            )

        return self


@lru_cache
def get_settings() -> Settings:
    """Singleton: Chỉ khởi tạo Settings một lần duy nhất."""
    return Settings()


# Shortcut để import nhanh
settings = get_settings()

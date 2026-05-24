"""
Outbound Port — Storage Service Interface.
Adapter thực tế ở: adapters/storage/r2_adapter.py (hoặc minio_adapter.py)
"""

from abc import ABC, abstractmethod


class IStorageService(ABC):
    """Abstract Port: Contract cho Object Storage (Cloudflare R2, MinIO, S3)."""

    @abstractmethod
    async def upload(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        *,
        is_public: bool = False,
    ) -> str:
        """
        Upload file và trả về URL để lưu vào DB.
        """
        ...

    @abstractmethod
    async def delete(self, file_url: str) -> None:
        """Xóa file khỏi storage theo URL."""
        ...

    @abstractmethod
    async def get_presigned_url(self, file_url: str, expires_in: int = 3600) -> str:
        """
        Tạo presigned URL tạm thời cho private files.
        Dùng khi file is_public=False.
        """
        ...

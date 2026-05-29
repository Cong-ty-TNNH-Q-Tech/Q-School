"""
Outbound Port: GeneratedAssetRepository
Theo Hexagonal Architecture — Interface thuần túy (ABC).
Use Case chỉ phụ thuộc vào Port này, không biết gì về SQLAlchemy.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.models.ai import GeneratedAsset


class GeneratedAssetRepository(ABC):

    @abstractmethod
    async def create(
        self,
        creator_id: uuid.UUID,
        asset_type: str,
        input_params: dict,
        output_content: dict,
    ) -> GeneratedAsset:  # pragma: no cover
        """Tạo mới một GeneratedAsset."""
        ...

    @abstractmethod
    async def get_by_id(
        self, asset_id: uuid.UUID
    ) -> GeneratedAsset | None:  # pragma: no cover
        """Lấy asset theo ID."""
        ...

    @abstractmethod
    async def list_by_creator(
        self,
        creator_id: uuid.UUID,
        cursor_created_at: datetime | None,
        cursor_id: uuid.UUID | None,
        limit: int,
    ) -> list[GeneratedAsset]:  # pragma: no cover
        """
        Cursor pagination: trả về `limit` assets của creator.
        Lấy các record CŨ HƠN cursor (created_at, id) theo thứ tự DESC.
        """
        ...

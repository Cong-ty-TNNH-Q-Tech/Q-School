"""
Driven Adapter: SQLAlchemyGeneratedAssetRepository
Implements GeneratedAssetRepository (Port) bằng SQLAlchemy async.
Kế thừa BaseRepository để dùng cursor_paginate(), create(), get_by_id() có sẵn.
Tầng này là nơi DUY NHẤT được phép dùng SQLAlchemy ORM.
"""

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.generated_asset_repository import (
    GeneratedAssetRepository,
)
from app.domain.models.ai import GeneratedAsset


class SQLAlchemyGeneratedAssetRepository(
    BaseRepository[GeneratedAsset], GeneratedAssetRepository
):  # pragma: no cover

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(GeneratedAsset, session)

    async def create(  # type: ignore[override]
        self,
        creator_id: uuid.UUID,
        asset_type: str,
        input_params: dict,
        output_content: dict,
    ) -> GeneratedAsset:
        return await super().create(
            creator_id=creator_id,
            asset_type=asset_type,
            input_params=input_params,
            output_content=output_content,
        )

    async def get_by_id(self, asset_id: uuid.UUID) -> GeneratedAsset | None:
        return await super().get_by_id(asset_id)

    async def list_by_creator(
        self,
        creator_id: uuid.UUID,
        cursor_created_at: datetime | None,
        cursor_id: uuid.UUID | None,
        limit: int,
    ) -> list[GeneratedAsset]:
        """
        Dùng BaseRepository.cursor_paginate() với filter creator_id.
        ascending=False: mới nhất trước (default).
        """
        rows = await self.cursor_paginate(
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
            limit=limit,
            filters=[GeneratedAsset.creator_id == creator_id],
            ascending=False,
        )
        return list(rows)

from uuid import UUID
from datetime import datetime
from typing import Sequence
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.ai_repository import IDocumentRepository
from app.domain.models.ai import Document, DocumentChunk

class DocumentSQLAlchemyRepository(BaseRepository[Document], IDocumentRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Document, db)

    async def get_by_id(self, document_id: UUID) -> Document | None:
        # We can just use the super class method since it handles soft deletes
        return await super().get_by_id(document_id)

    async def get_by_uploader(
        self, 
        uploader_id: UUID,
        cursor_created_at: datetime | None = None,
        cursor_id: UUID | None = None,
        limit: int = 20,
    ) -> Sequence[Document]:
        return await self.cursor_paginate(
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
            limit=limit,
            filters=[Document.uploader_id == uploader_id],
            ascending=False
        )

    async def create(self, uploader_id: UUID, filename: str, file_type: str, s3_url: str, **kwargs) -> Document:
        doc = Document(
            uploader_id=uploader_id,
            filename=filename,
            file_type=file_type,
            s3_url=s3_url,
            **kwargs
        )
        self.db.add(doc)
        await self.db.flush()
        return doc

    async def update_status(self, document: Document, status: str) -> Document:
        document.status = status
        return await super().update(document)

    async def soft_delete(self, document: Document) -> Document:
        return await super().delete(document.id)

    async def save_chunks(self, chunks: Sequence['DocumentChunk']) -> None:
        self.db.add_all(chunks)
        await self.db.flush()

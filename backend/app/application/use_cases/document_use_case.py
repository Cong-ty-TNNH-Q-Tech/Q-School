import uuid
from typing import BinaryIO

from app.application.ports.outbound.ai_repository import IDocumentRepository
from app.application.ports.outbound.storage_service import IStorageService
from app.domain.models.ai import Document
from app.entrypoints.celery_worker import ai_tasks

class DocumentUseCase:
    def __init__(self, doc_repo: IDocumentRepository, storage: IStorageService):
        self.doc_repo = doc_repo
        self.storage = storage

    async def upload_document(
        self,
        uploader_id: uuid.UUID,
        filename: str,
        content_type: str,
        file_bytes: bytes,
        is_public: bool = False,
    ) -> Document:
        
        # Determine file_type from content_type
        file_type = "image"
        if "pdf" in content_type.lower():
            file_type = "pdf"
        elif "word" in content_type.lower() or "document" in content_type.lower() or "docx" in content_type.lower():
            file_type = "docx"
        elif "image" not in content_type.lower():
            # fallback or reject
            raise ValueError(f"Unsupported content type: {content_type}")

        # Upload to Storage
        s3_url = await self.storage.upload(
            file_bytes=file_bytes,
            filename=filename,
            content_type=content_type,
            is_public=is_public,
        )

        # Save to DB
        doc = await self.doc_repo.create(
            uploader_id=uploader_id,
            filename=filename,
            file_type=file_type,
            s3_url=s3_url,
            is_public=is_public,
            status="pending"
        )

        # Enqueue Celery Task for background parsing
        ai_tasks.parse_document.delay(str(doc.id))

        return doc

    async def get_document(self, document_id: uuid.UUID) -> Document | None:
        return await self.doc_repo.get_by_id(document_id)

    async def list_documents(self, uploader_id: uuid.UUID) -> list[Document]:
        return await self.doc_repo.get_by_uploader(uploader_id)

    async def delete_document(self, document_id: uuid.UUID) -> Document | None:
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            return None
        return await self.doc_repo.soft_delete(doc)

import uuid
from datetime import datetime
from typing import BinaryIO, Sequence

from app.application.ports.outbound.ai_repository import IDocumentRepository, IAITaskRepository
from app.application.ports.outbound.storage_service import IStorageService
from app.application.ports.outbound.llm_service import ILLMService
from app.domain.models.ai import Document
from app.entrypoints.celery_worker import ai_tasks

class DocumentUseCase:
    def __init__(
        self,
        doc_repo: IDocumentRepository,
        storage: IStorageService,
        llm_service: ILLMService | None = None,
        ai_task_repo: IAITaskRepository | None = None,
    ):
        self.doc_repo = doc_repo
        self.storage = storage
        self.llm_service = llm_service
        self.ai_task_repo = ai_task_repo

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

    async def list_documents(
        self,
        uploader_id: uuid.UUID,
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = 20,
    ) -> Sequence[Document]:
        return await self.doc_repo.get_by_uploader(
            uploader_id, cursor_created_at, cursor_id, limit
        )

    async def delete_document(self, document_id: uuid.UUID) -> Document | None:
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            return None
        return await self.doc_repo.soft_delete(doc)

    async def parse_document_async(self, document_id: str, ai_task_id: str | None = None) -> dict:
        import io
        import asyncio
        from app.domain.models.ai import DocumentChunk

        if not self.llm_service or not self.ai_task_repo:
            raise RuntimeError("llm_service and ai_task_repo must be provided for parse_document_async")

        if ai_task_id:
            task = await self.ai_task_repo.get_by_id(uuid.UUID(ai_task_id))
            if task and task.status == "completed":
                return {"status": "already_completed"}
            if task:
                await self.ai_task_repo.update_status(task, "processing")

        doc = await self.doc_repo.get_by_id(uuid.UUID(document_id))
        if not doc:
            raise ValueError(f"Document {document_id} not found")

        if doc.status == "ready":
            return {"status": "already_parsed"}

        await self.doc_repo.update_status(doc, "parsing")

        try:
            file_bytes = await self.storage.download(doc.s3_url)

            text_content = ""
            if doc.file_type == "pdf":
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
            elif doc.file_type == "docx":
                import docx
                d = docx.Document(io.BytesIO(file_bytes))
                text_content = "\n".join([para.text for para in d.paragraphs])
            else:
                text_content = "Image parsing not supported yet."

            chunk_size = 1000
            chunks = [text_content[i:i+chunk_size] for i in range(0, len(text_content), chunk_size) if text_content[i:i+chunk_size].strip()]

            # Embed chunks
            sem = asyncio.Semaphore(5)
            async def bounded_embed(text_chunk):
                async with sem:
                    return await self.llm_service.embed(text_chunk)
            
            tasks = [bounded_embed(chunk) for chunk in chunks]
            embeddings = await asyncio.gather(*tasks)

            db_chunks = []
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                db_chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_text=chunk_text,
                    embedding_vector=embedding,
                    chunk_index=idx
                )
                db_chunks.append(db_chunk)

            await self.doc_repo.save_chunks(db_chunks)
            await self.doc_repo.update_status(doc, "ready")

            if ai_task_id:
                task = await self.ai_task_repo.get_by_id(uuid.UUID(ai_task_id))
                if task:
                    await self.ai_task_repo.update_status(
                        task, "completed", result_payload={"status": "success", "chunks_count": len(chunks)}
                    )

            return {"status": "success", "chunks_count": len(chunks)}
        except Exception as exc:
            await self.doc_repo.update_status(doc, "error")
            raise exc

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, Form, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, AIUserDep
from app.application.use_cases.document_use_case import DocumentUseCase
from app.adapters.database.document_repository import DocumentSQLAlchemyRepository
from app.adapters.storage.r2_adapter import R2StorageAdapter
from app.entrypoints.api_v1.schemas.document import DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])

def get_document_use_case(db: AsyncSession = Depends(get_db)) -> DocumentUseCase:
    repo = DocumentSQLAlchemyRepository(db)
    storage = R2StorageAdapter()
    return DocumentUseCase(doc_repo=repo, storage=storage)

DocumentUseCaseDep = Annotated[DocumentUseCase, Depends(get_document_use_case)]

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    user: AIUserDep,
    use_case: DocumentUseCaseDep,
    file: UploadFile = File(...),
    is_public: bool = Form(False),
):
    """
    Upload file (PDF, DOCX, Image) cho hệ thống RAG.
    Trả về HTTP 202 Accepted, file sẽ được xử lý ngầm (parse & embed).
    """
    try:
        file_bytes = await file.read()
        doc = await use_case.upload_document(
            uploader_id=user.id,
            filename=file.filename,
            content_type=file.content_type,
            file_bytes=file_bytes,
            is_public=is_public,
        )
        return doc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=list[DocumentResponse])
async def list_documents(user: AIUserDep, use_case: DocumentUseCaseDep):
    """Lấy danh sách tài liệu của user."""
    docs = await use_case.list_documents(user.id)
    return docs

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: uuid.UUID, user: AIUserDep, use_case: DocumentUseCaseDep):
    """Lấy chi tiết tài liệu."""
    doc = await use_case.get_document(document_id)
    if not doc or doc.uploader_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: uuid.UUID, user: AIUserDep, use_case: DocumentUseCaseDep):
    """Soft delete tài liệu."""
    doc = await use_case.get_document(document_id)
    if not doc or doc.uploader_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    await use_case.delete_document(document_id)

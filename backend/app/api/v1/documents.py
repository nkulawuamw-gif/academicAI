from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.document_service import DocumentService
from app.core.exceptions import BadRequestException
from typing import Optional

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename:
        raise BadRequestException("No file provided")

    service = DocumentService(db)
    doc = await service.upload_document(current_user.id, file.file, file.filename)

    return {
        "id": str(doc.id),
        "filename": doc.original_filename,
        "file_type": doc.file_type.value if hasattr(doc.file_type, 'value') else doc.file_type,
        "file_size": doc.file_size,
        "status": doc.processing_status.value if hasattr(doc.processing_status, 'value') else doc.processing_status,
        "created_at": doc.created_at,
    }


@router.get("/")
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(db)
    docs = await service.get_user_documents(current_user.id)
    return [
        {
            "id": str(d.id),
            "filename": d.original_filename,
            "file_type": d.file_type.value if hasattr(d.file_type, 'value') else d.file_type,
            "file_size": d.file_size,
            "status": d.processing_status.value if hasattr(d.processing_status, 'value') else d.processing_status,
            "created_at": d.created_at,
        }
        for d in docs
    ]


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(db)
    doc = await service.get_document(document_id, current_user.id)
    return {
        "id": str(doc.id),
        "filename": doc.original_filename,
        "file_type": doc.file_type.value if hasattr(doc.file_type, 'value') else doc.file_type,
        "file_size": doc.file_size,
        "status": doc.processing_status.value if hasattr(doc.processing_status, 'value') else doc.processing_status,
        "content_preview": doc.content[:1000] if doc.content else None,
        "page_count": doc.page_count,
        "chunk_count": len(doc.chunks),
        "created_at": doc.created_at,
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(db)
    await service.delete_document(document_id, current_user.id)
    return {"message": "Document deleted"}


@router.post("/{document_id}/ask")
async def ask_document(
    document_id: str,
    question: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(db)
    answer = await service.ask_question(document_id, current_user.id, question)
    return {"question": question, "answer": answer}

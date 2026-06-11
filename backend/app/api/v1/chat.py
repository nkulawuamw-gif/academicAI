import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.chat import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    ConversationListResponse, MessageCreate, MessageResponse, AttachmentInfo,
)
from app.api.deps import get_current_user
from app.models.user import User
from app.services.chat_service import ChatService
from app.config import settings
from fastapi.responses import StreamingResponse
from loguru import logger
import json

router = APIRouter(prefix="/chat", tags=["Chat"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "uploads", "chat")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".pdf", ".docx", ".txt", ".csv", ".xlsx", ".pptx", ".md", ".py", ".js", ".ts", ".tsx", ".json", ".yaml", ".yml"}


@router.post("/upload")
async def upload_chat_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "file")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")

    file_id = str(uuid.uuid4())
    safe_name = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "file_name": file.filename,
        "file_url": f"/api/v1/chat/files/{safe_name}",
        "file_type": ext.lstrip("."),
        "file_size": len(content),
    }


@router.get("/files/{file_name}")
async def serve_chat_file(file_name: str):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    return await service.get_conversations(current_user.id, page, per_page)


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    conv = await service.create_conversation(current_user.id, request.title, request.context)
    return ConversationResponse(
        id=str(conv.id), title=conv.title, context=conv.context,
        is_active=conv.is_active, created_at=conv.created_at,
        updated_at=conv.updated_at, message_count=0,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    conv = await service.get_conversation(conversation_id, current_user.id)
    messages = await service.get_messages(conversation_id, current_user.id)
    return ConversationResponse(
        id=str(conv.id), title=conv.title, context=conv.context,
        is_active=conv.is_active, created_at=conv.created_at,
        updated_at=conv.updated_at, message_count=len(messages),
        last_message=messages[-1].content[:200] if messages else None,
    )


@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    request: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    conv = await service.update_conversation(conversation_id, current_user.id, request.title, request.context)
    return ConversationResponse(
        id=str(conv.id), title=conv.title, context=conv.context,
        is_active=conv.is_active, created_at=conv.created_at,
        updated_at=conv.updated_at,
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    await service.delete_conversation(conversation_id, current_user.id)
    return {"message": "Conversation deleted"}


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    messages = await service.get_messages(conversation_id, current_user.id)
    return [
        MessageResponse(
            id=str(m.id), conversation_id=str(m.conversation_id),
            role=m.role.value if hasattr(m.role, 'value') else m.role,
            content=m.content, metadata=m.extra_data,
            attachments=(m.extra_data or {}).get("attachments"),
            tokens_used=m.tokens_used, created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    request: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)
    return await service.send_message(conversation_id, current_user.id, request.content, request.metadata, request.attachments)


@router.post("/conversations/{conversation_id}/stream")
async def stream_message(
    conversation_id: str,
    request: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ChatService(db)

    async def generate():
        async for chunk in service.stream_message(conversation_id, current_user.id, request.content):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class AttachmentInfo(BaseModel):
    file_name: str
    file_url: str
    file_type: str
    file_size: int


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    metadata: Optional[dict] = None
    attachments: Optional[list[AttachmentInfo]] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    metadata: Optional[dict] = None
    attachments: Optional[list[AttachmentInfo]] = None
    tokens_used: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    context: Optional[dict] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    context: Optional[dict] = None


class ConversationResponse(BaseModel):
    id: str
    title: str
    context: Optional[dict] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int
    page: int
    per_page: int

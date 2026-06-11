from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.writing import WritingRequest, WritingResponse, OutlineRequest, OutlineResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.services.writing_service import WritingService
from datetime import datetime, timezone

router = APIRouter(prefix="/writing", tags=["Writing"])


@router.post("/generate", response_model=WritingResponse)
async def generate_writing(
    request: WritingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WritingService(db)
    result = await service.generate_writing(
        prompt=request.prompt,
        type=request.type,
        length=request.length,
        tone=request.tone,
        additional_instructions=request.additional_instructions,
    )
    return WritingResponse(
        title=result["title"],
        content=result["content"],
        word_count=result["word_count"],
        type=result["type"],
        generated_at=datetime.now(timezone.utc),
    )


@router.post("/outline", response_model=OutlineResponse)
async def generate_outline(
    request: OutlineRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WritingService(db)
    return await service.generate_outline(
        topic=request.topic,
        sections=request.sections,
        depth=request.depth,
    )

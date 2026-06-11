from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.paraphrase import ParaphraseRequest, ParaphraseResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.services.paraphrase_service import ParaphraseService

router = APIRouter(prefix="/paraphrase", tags=["Paraphrasing"])


@router.post("/", response_model=ParaphraseResponse)
async def paraphrase_text(
    request: ParaphraseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ParaphraseService(db)
    return await service.paraphrase(
        text=request.text,
        mode=request.mode,
        intensity=request.intensity,
    )

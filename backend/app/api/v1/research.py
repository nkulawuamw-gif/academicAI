from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.research import ResearchRequest, ResearchResponse, LiteratureReviewRequest, LiteratureReviewResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.services.research_service import ResearchService
from datetime import datetime, timezone

router = APIRouter(prefix="/research", tags=["Research"])


@router.post("/search", response_model=ResearchResponse)
async def research_search(
    request: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResearchService(db)
    return await service.research(
        query=request.query,
        max_sources=request.max_sources,
        include_summary=request.include_summary,
        include_citations=request.include_citations,
    )


@router.post("/literature-review", response_model=LiteratureReviewResponse)
async def generate_literature_review(
    request: LiteratureReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResearchService(db)
    return await service.generate_literature_review(
        topic=request.topic,
        sources=request.sources,
        format_type=request.format,
    )

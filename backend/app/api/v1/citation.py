from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.citation import (
    CitationCreateRequest, CitationGenerateRequest, CitationResponse, CitationListResponse,
)
from app.api.deps import get_current_user
from app.models.user import User
from app.services.citation_service import CitationService

router = APIRouter(prefix="/citations", tags=["Citations"])


@router.post("/generate")
async def generate_citation(
    request: CitationGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CitationService(db)
    citation_text = await service.generate_citation(request.style, request.source_text)
    return {"citation_text": citation_text, "style": request.style}


@router.post("/", response_model=CitationResponse)
async def create_citation(
    request: CitationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CitationService(db)
    citation = await service.create_citation(
        user_id=current_user.id,
        style=request.style,
        title=request.title,
        authors=request.authors,
        year=request.year,
        source_type=request.source_type,
        journal=request.journal,
        volume=request.volume,
        issue=request.issue,
        pages=request.pages,
        publisher=request.publisher,
        doi=request.doi,
        url=request.url,
    )
    return CitationResponse(
        id=str(citation.id), style=citation.style.value,
        citation_text=citation.citation_text, title=citation.title,
        authors=citation.authors, year=citation.year,
        created_at=citation.created_at,
    )


@router.get("/", response_model=CitationListResponse)
async def list_citations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CitationService(db)
    return await service.get_citations(current_user.id, page, per_page)

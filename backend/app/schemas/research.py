from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3)
    max_sources: int = Field(default=10, ge=1, le=50)
    include_summary: bool = True
    include_citations: bool = True


class SourceResponse(BaseModel):
    title: str
    url: str
    authors: Optional[list[str]] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    abstract: Optional[str] = None
    relevance_score: float = 0.0


class ResearchResponse(BaseModel):
    query: str
    summary: Optional[str] = None
    sources: list[SourceResponse]
    citations: Optional[list[dict]] = None


class LiteratureReviewRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    sources: list[str] = Field(..., min_length=1)
    format: str = Field(default="narrative", pattern="^(narrative|systematic|scoping)$")


class LiteratureReviewResponse(BaseModel):
    topic: str
    introduction: str
    sections: list[dict]
    conclusion: str
    references: list[str]
    generated_at: datetime

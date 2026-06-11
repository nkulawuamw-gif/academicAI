from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class CitationCreateRequest(BaseModel):
    style: str = Field(default="apa", pattern="^(apa|mla|harvard|chicago|ieee)$")
    title: str = Field(..., max_length=500)
    authors: Optional[str] = None
    year: Optional[int] = None
    source_type: Optional[str] = Field(None, pattern="^(book|journal|website|conference|thesis|report|other)$")
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    accessed_date: Optional[str] = None


class CitationGenerateRequest(BaseModel):
    style: str = Field(default="apa", pattern="^(apa|mla|harvard|chicago|ieee)$")
    source_text: str = Field(..., min_length=10)


class CitationResponse(BaseModel):
    id: str
    style: str
    citation_text: str
    title: str
    authors: Optional[str] = None
    year: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CitationListResponse(BaseModel):
    citations: list[CitationResponse]
    total: int

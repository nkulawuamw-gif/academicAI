from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class WritingRequest(BaseModel):
    prompt: str = Field(..., min_length=3)
    type: str = Field(default="essay", pattern="^(essay|report|research_paper|assignment|outline)$")
    length: str = Field(default="medium", pattern="^(short|medium|long)$")
    tone: str = Field(default="academic", pattern="^(academic|formal|informative|persuasive)$")
    additional_instructions: Optional[str] = None


class OutlineRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    sections: int = Field(default=5, ge=3, le=20)
    depth: str = Field(default="detailed", pattern="^(basic|detailed|comprehensive)$")


class OutlineResponse(BaseModel):
    topic: str
    outline: list[dict]
    suggested_sources: Optional[list[str]] = None


class WritingResponse(BaseModel):
    title: str
    content: str
    word_count: int
    type: str
    generated_at: datetime

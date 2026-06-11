from pydantic import BaseModel, Field
from typing import Optional


class ParaphraseRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=10000)
    mode: str = Field(default="academic", pattern="^(academic|professional|simplification|creative|humanize)$")
    intensity: str = Field(default="moderate", pattern="^(light|moderate|heavy)$")


class ParaphraseResponse(BaseModel):
    original_text: str
    paraphrased_text: str
    mode: str
    word_count_original: int
    word_count_paraphrased: int
    changes_made: int

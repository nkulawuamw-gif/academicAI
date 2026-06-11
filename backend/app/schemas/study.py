from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime, date


class QuizGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    question_count: int = Field(default=10, ge=5, le=50)
    question_types: Optional[list[str]] = None


class QuizQuestionResponse(BaseModel):
    id: str
    question_type: str
    question_text: str
    options: Optional[list] = None
    correct_answer: str
    explanation: Optional[str] = None
    points: int
    order: int

    class Config:
        from_attributes = True


class QuizResponse(BaseModel):
    id: str
    title: str
    topic: str
    difficulty: str
    question_count: int
    score: Optional[int] = None
    total_points: Optional[int] = None
    questions: list[QuizQuestionResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class QuizAnswerSubmission(BaseModel):
    answers: dict


class QuizResultResponse(BaseModel):
    quiz_id: str
    score: int
    total_points: int
    percentage: float
    answers: dict


class FlashcardGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    count: int = Field(default=10, ge=5, le=100)


class FlashcardResponse(BaseModel):
    id: str
    front: str
    back: str
    difficulty: str

    class Config:
        from_attributes = True


class FlashcardSetResponse(BaseModel):
    id: str
    title: str
    topic: str
    flashcards: list[FlashcardResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class NoteSummarizeRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=50000)
    format: str = Field(default="bullets", pattern="^(bullets|paragraphs|outline)$")
    detail_level: str = Field(default="moderate", pattern="^(concise|moderate|detailed)$")


class NoteSummarizeResponse(BaseModel):
    original_length: int
    summary_length: int
    summary: str
    key_points: list[str]


class StudyPlanGenerateRequest(BaseModel):
    subject: str = Field(..., min_length=3)
    start_date: date
    end_date: date
    hours_per_day: float = Field(default=2.0, ge=0.5, le=12)
    topics: Optional[list[str]] = None


class StudyTaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    scheduled_date: date
    duration_minutes: int
    is_completed: bool
    order: int

    class Config:
        from_attributes = True


class StudyPlanResponse(BaseModel):
    id: str
    title: str
    subject: str
    start_date: date
    end_date: date
    hours_per_day: float
    tasks: list[StudyTaskResponse]
    created_at: datetime

    class Config:
        from_attributes = True

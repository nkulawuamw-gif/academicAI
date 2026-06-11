from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class UserAdminResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    auth_provider: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    conversation_count: int = 0
    document_count: int = 0

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: list[UserAdminResponse]
    total: int
    page: int
    per_page: int


class AnalyticsResponse(BaseModel):
    total_users: int
    active_users_today: int
    total_conversations: int
    total_documents: int
    total_citations: int
    total_quizzes: int
    api_usage_today: int
    users_by_day: list[dict]
    feature_usage: dict


class ApiUsageResponse(BaseModel):
    total_requests: int
    requests_by_endpoint: dict
    requests_by_user: dict
    requests_by_day: list[dict]
    average_response_time: float
    error_rate: float

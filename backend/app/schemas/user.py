from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class UserProfileResponse(BaseModel):
    id: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    institution: Optional[str] = None
    course: Optional[str] = None
    year_of_study: Optional[int] = None
    preferences: Optional[dict] = None

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    institution: Optional[str] = None
    course: Optional[str] = None
    year_of_study: Optional[int] = None
    preferences: Optional[dict] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    auth_provider: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    profile: Optional[UserProfileResponse] = None

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)

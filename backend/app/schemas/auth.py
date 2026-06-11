from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., max_length=255)


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=128)


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., max_length=255)


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=8, max_length=128)


class GoogleAuthRequest(BaseModel):
    code: str


class AuthResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_verified: bool
    access_token: str
    refresh_token: str

    class Config:
        from_attributes = True

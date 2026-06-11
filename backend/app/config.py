from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./academic_assistant.db"

    # Auth
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/google/callback"

    # LLM Providers (free tiers available)
    LLM_PROVIDER: str = "auto"  # auto, openai, gemini, groq, ollama
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000

    # Frontend / CORS
    NEXT_PUBLIC_FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: str = ""  # comma-separated, e.g. "https://site1.com,https://site2.com"

    # General
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.core.logging import setup_logging
from app.database import init_db
from app.api.v1 import auth, chat, research, writing, paraphrase, citation, study, documents, admin
from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting AI Academic Assistant API...")
    if settings.ENVIRONMENT != "testing":
        await init_db()
    yield
    logger.info("Shutting down AI Academic Assistant API...")


app = FastAPI(
    title="AI Academic Assistant API",
    description="A comprehensive AI-powered academic assistant with chat, research, writing, and study tools",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.NEXT_PUBLIC_FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(research.router, prefix="/api/v1")
app.include_router(writing.router, prefix="/api/v1")
app.include_router(paraphrase.router, prefix="/api/v1")
app.include_router(citation.router, prefix="/api/v1")
app.include_router(study.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "service": "AI Academic Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/api/v1/health")
async def api_health():
    return {"status": "ok", "version": "1.0.0"}

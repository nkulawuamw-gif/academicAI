import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database import Base
from app.models import *
from app.main import app
from httpx import AsyncClient, ASGITransport


@pytest_asyncio.fixture
def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
    return engine


@pytest_asyncio.fixture
async def test_session(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(test_engine, class_=AsyncSession)() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

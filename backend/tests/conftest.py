import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import os

from app.main import app
from app.database import Base, get_db

# Use the provided DATABASE_URL if in CI, otherwise use a local dev database
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://poetry:poetry_secret_123@localhost:5432/poetry_bot_test")

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
async_session_test = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="function")
async def setup_db():
    """Create and drop all tables before and after each test."""
    from sqlalchemy import text
    async with engine_test.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture to provide a database session for tests."""
    async with async_session_test() as session:
        yield session

@pytest.fixture
async def client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Fixture to provide an AsyncClient for FastAPI endpoint testing."""
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Clean up override
    app.dependency_overrides.clear()

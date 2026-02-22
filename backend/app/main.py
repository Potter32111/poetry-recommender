"""Poetry Recommender Backend — FastAPI Application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.database import engine
from app.models.user import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Poetry Recommender API",
    description="API for a conversational poem recommendation and memorization system.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

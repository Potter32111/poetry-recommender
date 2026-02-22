"""Poetry Recommender Backend — FastAPI Application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.database import engine, Base
import app.models  # noqa: F401 — ensure all models registered with Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Alembic handles database migrations now, so no Base.metadata.create_all
    yield


app = FastAPI(
    title="Poetry Recommender API",
    description="API for a conversational poem recommendation and memorization system.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

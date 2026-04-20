"""Poetry Recommender Backend — FastAPI Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.database import engine, Base
import app.models  # noqa: F401 — ensure all models registered with Base
from app.services.ml import ml_service
from app.worker import start_worker

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Alembic handles database migrations now, so no Base.metadata.create_all
    start_worker()
    try:
        await ml_service.ensure_loaded()
    except Exception as e:
        logger.warning("Failed to pre-load ML model: %s", e)
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

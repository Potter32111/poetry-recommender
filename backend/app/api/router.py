"""API router aggregator."""

from fastapi import APIRouter
from app.api.users import router as users_router
from app.api.poems import router as poems_router
from app.api.memorization import router as memorization_router

router = APIRouter(prefix="/api/v1")
router.include_router(users_router)
router.include_router(poems_router)
router.include_router(memorization_router)

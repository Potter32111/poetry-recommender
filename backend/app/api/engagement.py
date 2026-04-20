"""Engagement API endpoints: achievements, daily challenges, TTS."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.poem import Poem
from app.services.achievements import get_all_badges_for_user
from app.services.daily_challenge import get_or_create_today_challenge
from app.services import tts

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/engagement", tags=["engagement"])


async def _get_user(telegram_id: int, db: AsyncSession) -> User:
    query = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ─── Achievements ────────────────────────────────────────────

@router.get("/achievements/{telegram_id}")
async def get_achievements(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """Return all badges with unlock status for the user."""
    user = await _get_user(telegram_id, db)
    return await get_all_badges_for_user(user.id, db)


# ─── Daily Challenges ───────────────────────────────────────

@router.get("/challenges/{telegram_id}/today")
async def get_today_challenge(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """Return today's challenge (creating one if needed)."""
    user = await _get_user(telegram_id, db)
    challenge = await get_or_create_today_challenge(user, db)
    await db.commit()
    return challenge


# ─── TTS ─────────────────────────────────────────────────────

@router.post("/poems/{poem_id}/tts")
async def poem_tts(poem_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Generate TTS audio for a poem. Returns MP3 bytes."""
    poem_q = select(Poem).where(Poem.id == poem_id)
    result = await db.execute(poem_q)
    poem = result.scalar_one_or_none()
    if not poem:
        raise HTTPException(status_code=404, detail="Poem not found")

    mp3_bytes = tts.synthesize(poem.text, poem.language)
    if mp3_bytes is None:
        raise HTTPException(status_code=400, detail="Poem is too long for TTS (>50 lines)")

    return Response(content=mp3_bytes, media_type="audio/mpeg")

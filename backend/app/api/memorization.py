"""Memorization & recommendation API endpoints."""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.memorization import Memorization
from app.models.poem import Poem
from app.schemas.memorization import MemorizationResponse, ReviewRequest
from app.schemas.poem import PoemResponse
from app.schemas.voice import VoiceCheckResponse
from app.services.spaced_rep import calculate_sm2
from app.services.recommender import get_poems_due_for_review, recommend_new_poem
from app.services import voice_evaluator

logger = logging.getLogger(__name__)

_ALLOWED_CONTENT_TYPES = {"audio/", "application/octet-stream", "video/ogg"}
_MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10 MB

def _update_user_gamification(user: User, xp_gain: int):
    """Update user XP, level, and streak based on activity."""
    # 1. Update XP and Level
    user.xp += xp_gain
    
    # Calculate next level threshold: next_level_xp = current_level * 100
    # Allow multiple level ups if XP gain is huge
    while user.xp >= (user.level * 100):
        user.xp -= (user.level * 100)
        user.level += 1
        
    # 2. Update Streak
    today = datetime.now(timezone.utc).date()
    if user.last_activity_date:
        delta_days = (today - user.last_activity_date).days
        if delta_days == 1:
            user.streak += 1 # Continue streak
        elif delta_days > 1:
            user.streak = 1 # Reset streak
        # If delta_days == 0, leave streak as is (already active today)
    else:
        user.streak = 1 # First activity ever
        
    user.last_activity_date = today

router = APIRouter(prefix="/memorization", tags=["memorization"])


@router.post("/recommend/{telegram_id}", response_model=PoemResponse)
async def recommend_poem(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """Recommend a poem for the user: either due-for-review or new."""
    user = await _get_user(telegram_id, db)

    # First check for poems due for review
    due = await get_poems_due_for_review(db, user.id)
    if due:
        mem = due[0]
        await db.refresh(mem, ["poem"])
        return mem.poem

    # If nothing due, recommend a new poem
    poem = await recommend_new_poem(db, user.id, user.language_pref)
    if not poem:
        raise HTTPException(status_code=404, detail="No more poems available")

    # Create memorization record
    memorization = Memorization(user_id=user.id, poem_id=poem.id, status="new")
    db.add(memorization)
    await db.commit()

    return poem


@router.post("/review/{telegram_id}/{poem_id}", response_model=MemorizationResponse)
async def review_poem(
    telegram_id: int,
    poem_id: uuid.UUID,
    data: ReviewRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit a review score (0-5) for a poem and update SM-2 schedule."""
    user = await _get_user(telegram_id, db)

    query = select(Memorization).where(
        Memorization.user_id == user.id, Memorization.poem_id == poem_id
    )
    result = await db.execute(query)
    mem = result.scalar_one_or_none()
    if not mem:
        # Auto-create memorization record (user reviewing a poem they got via recommendations)
        poem_check = await db.execute(select(Poem).where(Poem.id == poem_id))
        if not poem_check.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Poem not found")
        mem = Memorization(user_id=user.id, poem_id=poem_id, status="new")
        db.add(mem)
        await db.flush()

    # Calculate SM-2
    sm2 = calculate_sm2(
        quality=data.score,
        repetitions=mem.repetitions,
        ease_factor=mem.ease_factor,
        interval_days=mem.interval_days,
    )

    # Update record
    mem.ease_factor = sm2.ease_factor
    mem.interval_days = sm2.interval_days
    mem.repetitions = sm2.repetitions
    mem.next_review_at = sm2.next_review_at
    mem.last_reviewed_at = datetime.now(timezone.utc)
    mem.status = sm2.status

    # Append to score history
    history = mem.score_history or []
    history.append({"date": datetime.now(timezone.utc).isoformat(), "score": data.score})
    mem.score_history = history

    # Update Gamification (+15 XP for a review)
    _update_user_gamification(user, 15)

    await db.commit()
    await db.refresh(mem)
    return mem


@router.get("/progress/{telegram_id}")
async def get_progress(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """Get user's memorization stats."""
    user = await _get_user(telegram_id, db)

    query = select(Memorization).where(Memorization.user_id == user.id)
    result = await db.execute(query)
    mems = list(result.scalars().all())

    stats = {"new": 0, "learning": 0, "reviewing": 0, "memorized": 0, "total": len(mems)}
    for m in mems:
        stats[m.status] = stats.get(m.status, 0) + 1

    now = datetime.now(timezone.utc)
    due_count = sum(1 for m in mems if m.next_review_at and m.next_review_at <= now)
    stats["due_for_review"] = due_count

    return stats


@router.get("/due/all", tags=["scheduler"])
async def get_all_due_reviews(db: AsyncSession = Depends(get_db)):
    """Get telegram_ids of all users who have poems due for review right now. (For Scheduler)"""
    now = datetime.now(timezone.utc)
    # Select distinct user_ids where next_review_at <= now
    query = (
        select(Memorization.user_id)
        .where(Memorization.next_review_at <= now)
        .distinct()
    )
    result = await db.execute(query)
    due_user_ids = list(result.scalars().all())

    if not due_user_ids:
        return []

    # Count due poems per user
    due_counts_q = (
        select(Memorization.user_id, func.count(Memorization.id).label("due_count"))
        .where(Memorization.next_review_at <= now)
        .group_by(Memorization.user_id)
    )
    due_counts_result = await db.execute(due_counts_q)
    due_map = {row.user_id: row.due_count for row in due_counts_result}

    # Get their telegram_ids, ui_language, notification_time, streak
    user_query = select(
        User.id, User.telegram_id, User.ui_language, User.notification_time, User.streak
    ).where(User.id.in_(due_user_ids))
    user_result = await db.execute(user_query)

    users_with_due = [
        {
            "telegram_id": row.telegram_id,
            "ui_language": row.ui_language,
            "notification_time": row.notification_time,
            "streak": row.streak,
            "due_count": due_map.get(row.id, 0),
        }
        for row in user_result
    ]
    return users_with_due


@router.get("/due/{telegram_id}", response_model=list[MemorizationResponse])
async def get_due_reviews(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """Get all poems due for review."""
    user = await _get_user(telegram_id, db)
    due = await get_poems_due_for_review(db, user.id)
    return due


@router.post("/check-voice/{telegram_id}/{poem_id}", response_model=VoiceCheckResponse)
async def check_voice(
    telegram_id: int,
    poem_id: uuid.UUID,
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Accept a voice message, transcribe, compare with poem, and update SM-2."""
    user = await _get_user(telegram_id, db)

    # Load poem
    poem_query = select(Poem).where(Poem.id == poem_id)
    poem_result = await db.execute(poem_query)
    poem = poem_result.scalar_one_or_none()
    if not poem:
        raise HTTPException(status_code=404, detail="Poem not found")

    # Get or create memorization record
    mem_query = select(Memorization).where(
        Memorization.user_id == user.id, Memorization.poem_id == poem_id
    )
    mem_result = await db.execute(mem_query)
    mem = mem_result.scalar_one_or_none()
    if not mem:
        # Auto-create memorization record (user reviewing a poem they got via recommendations)
        poem_check = await db.execute(select(Poem).where(Poem.id == poem_id))
        if not poem_check.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Poem not found")
        mem = Memorization(user_id=user.id, poem_id=poem_id, status="new")
        db.add(mem)
        await db.flush()

    # Validate audio upload
    content_type = audio.content_type or ""
    if not (
        content_type.startswith("audio/")
        or content_type == "application/octet-stream"
        or content_type == "video/ogg"
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content type '{content_type}'. Expected audio file.",
        )

    audio_bytes = await audio.read()
    if len(audio_bytes) > _MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Audio file too large. Maximum size is 10 MB.",
        )

    # Evaluate voice
    evaluation = await voice_evaluator.evaluate(audio_bytes, poem.text, poem.language)

    # Update SM-2
    sm2 = calculate_sm2(
        quality=evaluation.sm2_score,
        repetitions=mem.repetitions,
        ease_factor=mem.ease_factor,
        interval_days=mem.interval_days,
    )

    mem.ease_factor = sm2.ease_factor
    mem.interval_days = sm2.interval_days
    mem.repetitions = sm2.repetitions
    mem.next_review_at = sm2.next_review_at
    mem.last_reviewed_at = datetime.now(timezone.utc)
    mem.status = sm2.status

    # Append to score history
    history = mem.score_history or []
    history.append({
        "date": datetime.now(timezone.utc).isoformat(),
        "score": evaluation.sm2_score,
        "accuracy_percent": evaluation.accuracy_percent,
        "method": "voice",
    })
    mem.score_history = history

    # Update Gamification (+30 XP for a voice check)
    _update_user_gamification(user, 30)

    await db.commit()
    await db.refresh(mem)

    return VoiceCheckResponse(
        transcribed_text=evaluation.transcribed_text,
        accuracy_percent=evaluation.accuracy_percent,
        sm2_score=evaluation.sm2_score,
        missed_lines=evaluation.missed_lines,
        feedback=evaluation.feedback,
        next_steps=evaluation.next_steps,
        status=mem.status,
        interval_days=mem.interval_days,
    )


async def _get_user(telegram_id: int, db: AsyncSession) -> User:
    """Helper to get user by telegram_id or raise 404."""
    query = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

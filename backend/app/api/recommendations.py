import asyncio
import logging
import random
from typing import Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.poem import Poem
from app.models.user import User
from app.models.memorization import Memorization
from app.services.ml import ml_service
from app.services.parser import parser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

MAX_SKIPPED_POEMS = 20


def _weighted_sample(items: list, weights: list[float], k: int) -> list:
    """Weighted random sample without replacement."""
    items = list(items)
    weights = list(weights)
    selected = []
    for _ in range(min(k, len(items))):
        total = sum(weights)
        if total <= 0:
            break
        r = random.uniform(0, total)
        cumulative = 0.0
        for i, w in enumerate(weights):
            cumulative += w
            if cumulative >= r:
                selected.append(items[i])
                items.pop(i)
                weights.pop(i)
                break
    return selected


ERA_MAPPING = {
    "classic": ("", "1900"),
    "silver_age": ("1900", "1925"),
    "soviet": ("1925", "1991"),
    "modern": ("1991", ""),
}


@router.get("/", response_model=list[dict[str, Any]])
async def get_recommendations(
    telegram_id: int,
    mood: str | None = None,
    length: str | None = None,  # "short", "medium", "long", "any"
    era: str | None = None,  # "classic", "silver_age", "soviet", "modern"
    author: str | None = None,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
):
    """
    Get personalized poem recommendations using vector similarity.
    Factors: mood, temporal context, user history, difficulty progression.
    """
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. Gather User History
    memo_result = await db.execute(
        select(Poem)
        .join(Memorization, Memorization.poem_id == Poem.id)
        .where(Memorization.user_id == user.id)
    )
    memorized_poems = memo_result.scalars().all()
    memorized_ids = [str(p.id) for p in memorized_poems]

    # 2. Extract History Preferences
    authors = set(p.author for p in memorized_poems if p.author)
    fav_authors = list(authors)[:3]

    # 3. Difficulty progression based on experience
    memo_count = len(memorized_poems)
    if memo_count == 0:
        experience = "beginner"
    elif memo_count <= 5:
        experience = "intermediate"
    else:
        experience = "advanced"

    # 4. Determine Temporal Context
    now = datetime.now()
    hour = now.hour
    month = now.month

    if 5 <= hour < 12:
        time_of_day = "morning"
    elif 12 <= hour < 17:
        time_of_day = "afternoon"
    elif 17 <= hour < 22:
        time_of_day = "evening"
    else:
        time_of_day = "night"

    if month in (12, 1, 2):
        season = "winter"
    elif month in (3, 4, 5):
        season = "spring"
    elif month in (6, 7, 8):
        season = "summer"
    else:
        season = "autumn"

    # 5. Handle Length preference (track whether user explicitly set it)
    user_specified_length = length is not None and length != "any"
    if user_specified_length:
        user.preferences = {**user.preferences, "last_length": length}
    elif not length or length == "any":
        length = user.preferences.get("last_length", "any")

    # 6. Exclude memorized + skipped poems
    skipped_ids: list[str] = user.preferences.get("skipped_poems", [])
    exclude_ids = memorized_ids + skipped_ids

    # 7. Build context prompt and determine recommendation reason
    # Mood is ONLY used when explicitly provided — no persistence
    reason_key = "discover"
    reason_args: dict[str, str] = {}

    if mood and mood.lower() != "surprise me":
        context_prompt = mood
        reason_key = "mood"
        reason_args = {"mood": mood}
    else:
        context_parts = [f"It is a {season} {time_of_day}."]
        if fav_authors:
            context_parts.append(f"The user enjoys poetry by {', '.join(fav_authors)}.")
        context_parts.append("The user wants a poem suitable for this moment.")
        context_prompt = " ".join(context_parts)
        reason_key = "time"
        reason_args = {"season": season, "time_of_day": time_of_day}

    # Enrich context prompt with era/author when provided
    if era and era in ERA_MAPPING:
        context_prompt += f" A {era.replace('_', ' ')} era poem."
    if author:
        context_prompt += f" By {author}."

    logger.info(f"Context Prompt for {telegram_id}: {context_prompt}")

    # 8. Generate embedding
    try:
        composite_vector = await ml_service.generate_embedding(context_prompt)
    except Exception as e:
        logger.error(f"ML embedding generation failed: {e}")
        composite_vector = None

    # 9. Real-time scraping (if mood provided)
    if mood:
        try:
            logger.info(f"Triggering real-time search for mood: {mood}")
            await asyncio.wait_for(parser.search_and_parse(mood, limit=4), timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Real-time search timed out after 10s")
        except Exception as e:
            logger.error(f"Real-time search failed: {e}")

    # 10. Query PGVector using Cosine Distance
    recommendations: list[Poem] = []
    if composite_vector is not None:
        base_query = select(
            Poem, Poem.embedding.cosine_distance(composite_vector).label("dist")
        )
        base_query = base_query.where(Poem.embedding.is_not(None))

        if exclude_ids:
            base_query = base_query.where(Poem.id.notin_(exclude_ids))

        # Apply Length Filter
        if length == "short":
            base_query = base_query.where(Poem.lines_count <= 12)
        elif length == "medium":
            base_query = base_query.where(Poem.lines_count.between(13, 30))
        elif length == "long":
            base_query = base_query.where(Poem.lines_count > 30)

        # Apply Era Filter
        if era and era in ERA_MAPPING:
            base_query = base_query.where(
                Poem.era.ilike(f"%{era.replace('_', ' ')}%")
            )

        # Apply Author Filter
        if author:
            base_query = base_query.where(Poem.author.ilike(f"%{author}%"))

        # Apply difficulty progression as soft preference
        difficulty_query = base_query
        if experience == "beginner":
            difficulty_query = base_query.where(Poem.difficulty <= 2)
            if not user_specified_length:
                difficulty_query = difficulty_query.where(Poem.lines_count <= 16)
        elif experience == "intermediate":
            difficulty_query = base_query.where(Poem.difficulty <= 3.5)
            if not user_specified_length:
                difficulty_query = difficulty_query.where(Poem.lines_count <= 30)

        pool_size = max(limit * 4, 10)

        # Try difficulty-filtered first, fall back to unrestricted if not enough
        if experience != "advanced":
            rec_result = await db.execute(
                difficulty_query.order_by("dist").limit(pool_size)
            )
            results = list(rec_result.all())
            if len(results) < limit:
                rec_result = await db.execute(
                    base_query.order_by("dist").limit(pool_size)
                )
                results = list(rec_result.all())
        else:
            rec_result = await db.execute(
                base_query.order_by("dist").limit(pool_size)
            )
            results = list(rec_result.all())

        # Distance threshold: if all candidates are too far, fall back to random
        if results and all(r[1] > 1.5 for r in results):
            logger.warning(f"All candidates dist > 1.5 for {telegram_id}, falling back to random")
            results = []

        # Weighted sampling: closer matches get higher probability
        if results:
            sample_size = min(limit, len(results))
            max_dist = max(d for _, d in results)
            weights = [(max_dist - d + 0.1) for _, d in results]
            sampled = _weighted_sample(results, weights, sample_size)
            recommendations = [p for p, _ in sampled]

            # Refine reason: check if an author match is relevant
            if reason_key == "time" and fav_authors and recommendations:
                for rec in recommendations:
                    if rec.author in fav_authors:
                        reason_key = "author"
                        reason_args = {"author": rec.author}
                        break

            for p, dist in sampled:
                logger.info(f"SAMPLED: [{dist:.4f}] '{p.title}' (ID: {p.id})")

    # Fallback to random if no vector results
    if not recommendations:
        reason_key = "discover"
        reason_args = {}
        logger.warning("No vector results. Falling back to random.")
        fb_query = select(Poem)
        if exclude_ids:
            fb_query = fb_query.where(Poem.id.notin_(exclude_ids))

        if length == "short":
            fb_query = fb_query.where(Poem.lines_count <= 12)
        elif length == "medium":
            fb_query = fb_query.where(Poem.lines_count.between(13, 30))
        elif length == "long":
            fb_query = fb_query.where(Poem.lines_count > 30)

        if era and era in ERA_MAPPING:
            fb_query = fb_query.where(Poem.era.ilike(f"%{era.replace('_', ' ')}%"))
        if author:
            fb_query = fb_query.where(Poem.author.ilike(f"%{author}%"))

        fallback_result = await db.execute(fb_query.order_by(func.random()).limit(limit))
        recommendations = list(fallback_result.scalars().all())

    await db.commit()

    return [
        {
            "id": str(p.id),
            "title": p.title,
            "author": p.author,
            "language": p.language,
            "difficulty": p.difficulty,
            "lines_count": p.lines_count,
            "themes": p.themes,
            "era": p.era,
            "reason_key": reason_key,
            "reason_args": reason_args,
        }
        for p in recommendations
    ]


@router.post("/skip")
async def skip_poem(
    telegram_id: int,
    poem_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Record a skipped poem to avoid recommending it again soon."""
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    skipped: list[str] = user.preferences.get("skipped_poems", [])
    if poem_id not in skipped:
        skipped.append(poem_id)
    if len(skipped) > MAX_SKIPPED_POEMS:
        skipped = skipped[-MAX_SKIPPED_POEMS:]

    user.preferences = {**user.preferences, "skipped_poems": skipped}
    await db.commit()
    return {"status": "ok"}

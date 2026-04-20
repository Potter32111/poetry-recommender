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

        pool_size = max(limit * 4, 10)

        # Build filter chain ordered by priority — drop one filter at a time
        # if the result set is empty (soft filters).
        async def _query_with_filters(
            apply_length: bool, apply_era: bool, apply_author: bool, apply_difficulty: bool
        ) -> list:
            q = base_query
            if apply_length:
                if length == "short":
                    q = q.where(Poem.lines_count <= 12)
                elif length == "medium":
                    q = q.where(Poem.lines_count.between(13, 30))
                elif length == "long":
                    q = q.where(Poem.lines_count > 30)
            if apply_era and era and era in ERA_MAPPING:
                q = q.where(Poem.era.ilike(f"%{era.replace('_', ' ')}%"))
            if apply_author and author:
                q = q.where(Poem.author.ilike(f"%{author}%"))
            if apply_difficulty:
                if experience == "beginner":
                    q = q.where(Poem.difficulty <= 2)
                elif experience == "intermediate":
                    q = q.where(Poem.difficulty <= 3.5)
            r = await db.execute(q.order_by("dist").limit(pool_size))
            return list(r.all())

        # Try cascading: drop the most restrictive filters first if no results.
        attempts = [
            (True, True, True, experience != "advanced"),   # everything
            (True, True, True, False),                       # drop difficulty
            (True, True, False, False),                      # drop author
            (True, False, False, False),                     # drop era
            (False, False, False, False),                    # drop length too
        ]
        results: list = []
        for apply_len, apply_era, apply_auth, apply_diff in attempts:
            results = await _query_with_filters(apply_len, apply_era, apply_auth, apply_diff)
            if len(results) >= limit:
                break
        if not results:
            results = await _query_with_filters(False, False, False, False)

        # Distance threshold: only drop results if everything is far apart AND
        # we still have a comfortable pool size — otherwise keep what we have.
        if results and len(results) >= limit and all(r[1] > 1.8 for r in results):
            logger.warning(f"All candidates dist > 1.8 for {telegram_id}, falling back to random")
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

        async def _try_random(apply_length: bool, apply_era: bool, apply_author: bool) -> list:
            q = fb_query
            if apply_length:
                if length == "short":
                    q = q.where(Poem.lines_count <= 12)
                elif length == "medium":
                    q = q.where(Poem.lines_count.between(13, 30))
                elif length == "long":
                    q = q.where(Poem.lines_count > 30)
            if apply_era and era and era in ERA_MAPPING:
                q = q.where(Poem.era.ilike(f"%{era.replace('_', ' ')}%"))
            if apply_author and author:
                q = q.where(Poem.author.ilike(f"%{author}%"))
            r = await db.execute(q.order_by(func.random()).limit(limit))
            return list(r.scalars().all())

        for combo in [(True, True, True), (True, True, False), (True, False, False), (False, False, False)]:
            recommendations = await _try_random(*combo)
            if recommendations:
                break

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

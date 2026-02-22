"""Recommendation engine for selecting poems for users."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.poem import Poem
from app.models.memorization import Memorization


async def get_poems_due_for_review(
    db: AsyncSession, user_id: uuid.UUID
) -> list[Memorization]:
    """Get memorizations that are due for review."""
    now = datetime.now(timezone.utc)
    query = (
        select(Memorization)
        .where(
            Memorization.user_id == user_id,
            Memorization.next_review_at <= now,
            Memorization.status.in_(["learning", "reviewing"]),
        )
        .order_by(Memorization.next_review_at)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def recommend_new_poem(
    db: AsyncSession,
    user_id: uuid.UUID,
    language: str = "both",
) -> Poem | None:
    """Recommend a poem the user hasn't started memorizing yet.

    Filters by language preference and picks a random unseen poem.
    """
    # Get IDs of poems already assigned to this user
    known_poem_ids = select(Memorization.poem_id).where(Memorization.user_id == user_id)

    query = select(Poem).where(Poem.id.notin_(known_poem_ids))

    if language != "both":
        query = query.where(Poem.language == language)

    # Random selection
    query = query.order_by(func.random()).limit(1)

    result = await db.execute(query)
    return result.scalar_one_or_none()

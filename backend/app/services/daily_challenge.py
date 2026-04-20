"""Daily challenge creation and progress tracking."""

import logging
import random
from datetime import datetime, timezone, date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_challenge import DailyChallenge
from app.models.user import User

logger = logging.getLogger(__name__)

# Goal definitions: (goal_type, goal_target)
_GOAL_POOL: list[tuple[str, int]] = [
    ("review_n_poems", 3),
    ("memorize_one_stanza", 1),
    ("voice_recite_one", 1),
    ("learn_new_poem", 1),
]

_CHALLENGE_XP_BONUS = 50


async def get_or_create_today_challenge(
    user: User, db: AsyncSession
) -> dict:
    """Return today's challenge for the user, creating one if none exists."""
    today = date.today()
    q = select(DailyChallenge).where(
        DailyChallenge.user_id == user.id,
        DailyChallenge.date == today,
    )
    result = await db.execute(q)
    challenge = result.scalar_one_or_none()

    if challenge is None:
        goal_type, goal_target = random.choice(_GOAL_POOL)
        challenge = DailyChallenge(
            user_id=user.id,
            date=today,
            goal_type=goal_type,
            goal_target=goal_target,
        )
        db.add(challenge)
        await db.flush()

    return _to_dict(challenge)


async def update_challenge_progress(
    user: User, action: str, db: AsyncSession
) -> dict | None:
    """Increment challenge progress if action matches today's goal.

    action is one of: "review", "voice_recite", "text_recite", "learn_new", "memorize_stanza"
    Returns challenge dict if progress was made, None otherwise.
    """
    today = date.today()
    q = select(DailyChallenge).where(
        DailyChallenge.user_id == user.id,
        DailyChallenge.date == today,
    )
    result = await db.execute(q)
    challenge = result.scalar_one_or_none()
    if not challenge or challenge.completed_at:
        return None

    # Map actions to goal types
    matches = {
        "review": ["review_n_poems"],
        "voice_recite": ["review_n_poems", "voice_recite_one"],
        "text_recite": ["review_n_poems"],
        "learn_new": ["learn_new_poem"],
        "memorize_stanza": ["memorize_one_stanza"],
    }

    applicable_goals = matches.get(action, [])
    if challenge.goal_type not in applicable_goals:
        return None

    challenge.current_progress += 1

    # Check completion
    completed_now = False
    if challenge.current_progress >= challenge.goal_target and not challenge.completed_at:
        challenge.completed_at = datetime.now(timezone.utc)
        completed_now = True
        # Award bonus XP
        user.xp += _CHALLENGE_XP_BONUS

    result_dict = _to_dict(challenge)
    result_dict["just_completed"] = completed_now
    result_dict["bonus_xp"] = _CHALLENGE_XP_BONUS if completed_now else 0
    return result_dict


def _to_dict(ch: DailyChallenge) -> dict:
    return {
        "id": str(ch.id),
        "date": ch.date.isoformat(),
        "goal_type": ch.goal_type,
        "goal_target": ch.goal_target,
        "current_progress": ch.current_progress,
        "completed_at": ch.completed_at.isoformat() if ch.completed_at else None,
    }

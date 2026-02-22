"""SM-2 Spaced Repetition Algorithm.

Based on the SuperMemo SM-2 algorithm by P. Wozniak.
See: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
"""

from datetime import datetime, timedelta, timezone
from dataclasses import dataclass


@dataclass
class SM2Result:
    """Result of an SM-2 review calculation."""

    ease_factor: float
    interval_days: int
    repetitions: int
    next_review_at: datetime
    status: str  # "learning", "reviewing", "memorized"


def calculate_sm2(
    quality: int,
    repetitions: int,
    ease_factor: float,
    interval_days: int,
) -> SM2Result:
    """Calculate next review using SM-2 algorithm.

    Args:
        quality: Score from 0-5 (0=total blackout, 5=perfect recall).
        repetitions: Number of successful consecutive repetitions.
        ease_factor: Current ease factor (>= 1.3).
        interval_days: Current interval in days.

    Returns:
        SM2Result with updated parameters and next review date.
    """
    if quality < 0 or quality > 5:
        raise ValueError("Quality must be between 0 and 5")

    now = datetime.now(timezone.utc)

    if quality < 3:
        # Failed recall — reset
        repetitions = 0
        interval_days = 1
        status = "learning"
    else:
        # Successful recall
        if repetitions == 0:
            interval_days = 1
        elif repetitions == 1:
            interval_days = 6
        else:
            interval_days = round(interval_days * ease_factor)

        repetitions += 1

        # Update ease factor
        ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease_factor = max(1.3, ease_factor)

        if repetitions >= 5 and ease_factor >= 2.0:
            status = "memorized"
        else:
            status = "reviewing"

    next_review = now + timedelta(days=interval_days)

    return SM2Result(
        ease_factor=round(ease_factor, 2),
        interval_days=interval_days,
        repetitions=repetitions,
        next_review_at=next_review,
        status=status,
    )

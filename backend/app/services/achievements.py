"""Achievement / badge definitions and awarding logic."""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.memorization import Memorization
from app.models.achievement import UserAchievement
from app.models.poem import Poem

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BadgeDef:
    slug: str
    title_ru: str
    title_en: str
    description_ru: str
    description_en: str
    emoji: str


BADGES: list[BadgeDef] = [
    BadgeDef(
        slug="first_poem",
        title_ru="Первое стихотворение",
        title_en="First Poem",
        description_ru="Запомните своё первое стихотворение",
        description_en="Memorize your first poem",
        emoji="📖",
    ),
    BadgeDef(
        slug="streak_7",
        title_ru="Недельная серия",
        title_en="Week Streak",
        description_ru="7-дневная серия занятий",
        description_en="7-day learning streak",
        emoji="🔥",
    ),
    BadgeDef(
        slug="streak_30",
        title_ru="Месячная серия",
        title_en="Month Streak",
        description_ru="30-дневная серия занятий",
        description_en="30-day learning streak",
        emoji="🔥🔥",
    ),
    BadgeDef(
        slug="polyglot",
        title_ru="Полиглот",
        title_en="Polyglot",
        description_ru="Запомните стихи на EN и RU",
        description_en="Memorize poems in both EN and RU",
        emoji="🌍",
    ),
    BadgeDef(
        slug="marathon",
        title_ru="Марафонец",
        title_en="Marathon",
        description_ru="Запомните 50 стихов",
        description_en="Memorize 50 poems",
        emoji="🏃",
    ),
    BadgeDef(
        slug="voice_master",
        title_ru="Мастер голоса",
        title_en="Voice Master",
        description_ru="5 идеальных голосовых проверок (точность > 90%)",
        description_en="5 perfect voice recitations (accuracy > 90%)",
        emoji="🎤",
    ),
    BadgeDef(
        slug="early_bird",
        title_ru="Ранняя пташка",
        title_en="Early Bird",
        description_ru="Занимайтесь утром (6-9) 3 дня подряд",
        description_en="Review at 6-9 AM for 3 days",
        emoji="🐦",
    ),
    BadgeDef(
        slug="night_owl",
        title_ru="Сова",
        title_en="Night Owl",
        description_ru="Занимайтесь после 22:00 три дня подряд",
        description_en="Review after 22:00 for 3 days",
        emoji="🦉",
    ),
    BadgeDef(
        slug="pushkin_fan",
        title_ru="Фанат Пушкина",
        title_en="Pushkin Fan",
        description_ru="Запомните 3 стиха Пушкина",
        description_en="Memorize 3 Pushkin poems",
        emoji="👤",
    ),
]

BADGE_MAP: dict[str, BadgeDef] = {b.slug: b for b in BADGES}


async def check_and_award_badges(user: User, db: AsyncSession) -> list[str]:
    """Check all badge conditions and award any newly earned ones.

    Returns list of newly awarded badge slugs.
    """
    # Load already-earned slugs
    existing_q = select(UserAchievement.badge_slug).where(UserAchievement.user_id == user.id)
    existing_result = await db.execute(existing_q)
    earned: set[str] = set(existing_result.scalars().all())

    new_badges: list[str] = []

    # Gather memorization data once
    mem_q = select(Memorization).where(Memorization.user_id == user.id)
    mem_result = await db.execute(mem_q)
    mems = list(mem_result.scalars().all())

    memorized_mems = [m for m in mems if m.status == "memorized"]
    reviewed_mems = [m for m in mems if m.last_reviewed_at is not None]

    # 1. first_poem
    if "first_poem" not in earned and len(memorized_mems) >= 1:
        new_badges.append("first_poem")

    # 2. streak_7
    if "streak_7" not in earned and user.streak >= 7:
        new_badges.append("streak_7")

    # 3. streak_30
    if "streak_30" not in earned and user.streak >= 30:
        new_badges.append("streak_30")

    # 4. polyglot — memorized at least 1 EN and 1 RU poem
    if "polyglot" not in earned and memorized_mems:
        # Need poem languages
        poem_ids = [m.poem_id for m in memorized_mems]
        if poem_ids:
            lang_q = (
                select(Poem.language)
                .where(Poem.id.in_(poem_ids))
                .distinct()
            )
            lang_result = await db.execute(lang_q)
            langs = set(lang_result.scalars().all())
            if "en" in langs and "ru" in langs:
                new_badges.append("polyglot")

    # 5. marathon — 50 memorized
    if "marathon" not in earned and len(memorized_mems) >= 50:
        new_badges.append("marathon")

    # 6. voice_master — 5 entries with accuracy > 90% and method == voice
    if "voice_master" not in earned:
        voice_perfect = 0
        for m in reviewed_mems:
            for entry in (m.score_history or []):
                if (
                    isinstance(entry, dict)
                    and entry.get("method") == "voice"
                    and (entry.get("accuracy_percent", 0) or 0) > 90
                ):
                    voice_perfect += 1
        if voice_perfect >= 5:
            new_badges.append("voice_master")

    # 7. early_bird — check score_history for 3 different days with 6-9 AM entries
    if "early_bird" not in earned:
        early_days: set[str] = set()
        for m in reviewed_mems:
            for entry in (m.score_history or []):
                if isinstance(entry, dict) and entry.get("date"):
                    try:
                        dt = datetime.fromisoformat(entry["date"])
                        if 6 <= dt.hour < 9:
                            early_days.add(dt.date().isoformat())
                    except (ValueError, TypeError):
                        pass
        if len(early_days) >= 3:
            new_badges.append("early_bird")

    # 8. night_owl — 3 different days with entries after 22:00
    if "night_owl" not in earned:
        night_days: set[str] = set()
        for m in reviewed_mems:
            for entry in (m.score_history or []):
                if isinstance(entry, dict) and entry.get("date"):
                    try:
                        dt = datetime.fromisoformat(entry["date"])
                        if dt.hour >= 22:
                            night_days.add(dt.date().isoformat())
                    except (ValueError, TypeError):
                        pass
        if len(night_days) >= 3:
            new_badges.append("night_owl")

    # 9. pushkin_fan — 3 memorized Pushkin poems
    if "pushkin_fan" not in earned and memorized_mems:
        poem_ids = [m.poem_id for m in memorized_mems]
        if poem_ids:
            pushkin_q = select(func.count()).select_from(Poem).where(
                Poem.id.in_(poem_ids),
                func.lower(Poem.author).contains("пушкин")
                | func.lower(Poem.author).contains("pushkin"),
            )
            pushkin_result = await db.execute(pushkin_q)
            if (pushkin_result.scalar() or 0) >= 3:
                new_badges.append("pushkin_fan")

    # Persist newly earned badges
    for slug in new_badges:
        db.add(UserAchievement(user_id=user.id, badge_slug=slug))

    return new_badges


async def get_all_badges_for_user(
    user_id, db: AsyncSession
) -> list[dict]:
    """Return all badges with award status for a user."""
    earned_q = select(UserAchievement).where(UserAchievement.user_id == user_id)
    earned_result = await db.execute(earned_q)
    earned_map: dict[str, datetime] = {
        a.badge_slug: a.awarded_at for a in earned_result.scalars().all()
    }

    result = []
    for b in BADGES:
        awarded_at = earned_map.get(b.slug)
        result.append({
            "slug": b.slug,
            "title_ru": b.title_ru,
            "title_en": b.title_en,
            "description_ru": b.description_ru,
            "description_en": b.description_en,
            "emoji": b.emoji,
            "awarded_at": awarded_at.isoformat() if awarded_at else None,
        })
    return result

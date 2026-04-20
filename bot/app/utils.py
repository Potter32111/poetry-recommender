"""Shared utility functions for bot handlers."""

import logging
import re
import time
from difflib import SequenceMatcher

from app.services.api_client import api

logger = logging.getLogger(__name__)

_MD_ESCAPE_RE = re.compile(r"([_*`\[\]])")


def escape_md(text: str) -> str:
    """Escape Markdown-special characters in user content for Telegram."""
    return _MD_ESCAPE_RE.sub(r"\\\1", text)

_lang_cache: dict[int, tuple[str, float]] = {}
_LANG_CACHE_TTL = 300.0  # 5 minutes


def invalidate_lang_cache(telegram_id: int) -> None:
    """Remove cached language for a user (call after language change)."""
    _lang_cache.pop(telegram_id, None)


async def get_user_lang(telegram_id: int) -> str:
    """Get user's UI language from backend, defaulting to 'ru'."""
    now = time.monotonic()
    cached = _lang_cache.get(telegram_id)
    if cached is not None:
        lang, ts = cached
        if now - ts < _LANG_CACHE_TTL:
            return lang

    try:
        user = await api.get_user(telegram_id)
        lang = user.get("ui_language", "ru")
        _lang_cache[telegram_id] = (lang, now)
        return lang
    except Exception:
        return "ru"


def format_poem_card(poem: dict, max_len: int = 3500) -> str:
    """Format a poem dict into a Telegram-friendly card with metadata."""
    title = escape_md(poem.get("title", "???"))
    author = escape_md(poem.get("author", "???"))
    text = poem.get("text", "")

    if len(text) > max_len:
        cut = text[:max_len].rfind("\n")
        text = text[:cut if cut > 0 else max_len] + "\n..."

    text = escape_md(text)

    card = f"📖 **{title}**\n*{author}*\n\n{text}"

    # Add metadata footer
    meta_parts: list[str] = []
    lines_count = poem.get("lines_count")
    if lines_count:
        meta_parts.append(f"📏 {lines_count} lines")

    difficulty = poem.get("difficulty", 0)
    if difficulty > 0:
        stars = "⭐" * min(round(difficulty), 5)
        meta_parts.append(stars)

    themes = poem.get("themes", [])
    if themes and isinstance(themes, list):
        meta_parts.append("🏷️ " + ", ".join(escape_md(t) for t in themes[:3]))

    era = poem.get("era")
    if era:
        meta_parts.append(f"📅 {escape_md(era)}")

    if meta_parts:
        card += "\n\n" + " · ".join(meta_parts)

    return card


def split_stanzas(text: str) -> list[str]:
    """Split poem text into stanzas by double newline; fall back to 4-line chunks."""
    parts = [s.strip() for s in text.split("\n\n") if s.strip()]
    if len(parts) > 1:
        return parts
    # No double-newline separators: chunk by 4 lines
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if len(lines) <= 4:
        return ["\n".join(lines)]
    return ["\n".join(lines[i : i + 4]) for i in range(0, len(lines), 4)]


def build_xp_bar(xp: int, next_level_xp: int) -> str:
    """Build a visual XP progress bar like `[████████░░]` 80%."""
    pct = min(xp / next_level_xp * 100, 100) if next_level_xp > 0 else 0
    filled = round(pct / 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"`[{bar}]` {pct:.0f}%"


def build_stanza_progress(completed: set[int], total: int) -> str:
    """Build stanza progress bar like ✅✅⬜⬜."""
    parts = ["✅" if i in completed else "⬜" for i in range(total)]
    return "".join(parts)


def compare_stanza_text(expected: str, actual: str) -> float:
    """Compare expected stanza text against user input. Returns accuracy 0-100."""
    norm_expected = re.sub(r"[^\w\s]", "", expected.lower().strip())
    norm_expected = re.sub(r"\s+", " ", norm_expected)
    norm_actual = re.sub(r"[^\w\s]", "", actual.lower().strip())
    norm_actual = re.sub(r"\s+", " ", norm_actual)
    if not norm_expected:
        return 0.0
    ratio = SequenceMatcher(None, norm_expected, norm_actual).ratio()
    return round(ratio * 100, 1)


def _challenge_goal_text(goal_type: str, target: int, lang: str) -> str:
    """Translate a challenge goal_type into human-readable text."""
    from app.translations import t
    goal_map = {
        "review_n_poems": t("goal_review_n_poems", lang, n=target),
        "memorize_one_stanza": t("goal_memorize_one_stanza", lang),
        "voice_recite_one": t("goal_voice_recite_one", lang),
        "learn_new_poem": t("goal_learn_new_poem", lang),
    }
    return goal_map.get(goal_type, goal_type)


def format_celebration(
    xp: int,
    level_up: int | None,
    challenge_progress: dict | None,
    new_badges: list[dict],
    freeze_used: bool,
    freezes_left: int,
    lang: str,
) -> str:
    """Build a multi-line celebration message combining all gamification events."""
    from app.translations import t

    parts: list[str] = []

    # XP gain
    parts.append(t("msg_celebration_xp", lang, xp=xp))

    # Level up
    if level_up:
        parts.append(t("msg_celebration_level", lang, level=level_up))

    # Daily challenge
    if challenge_progress:
        line = t(
            "msg_celebration_challenge", lang,
            progress=challenge_progress.get("current_progress", 0),
            target=challenge_progress.get("goal_target", 1),
        )
        parts.append(line)
        if challenge_progress.get("just_completed"):
            parts.append(t("msg_challenge_completed", lang))

    # Badges
    for badge in new_badges:
        title_key = "title_ru" if lang == "ru" else "title_en"
        title = badge.get(title_key, badge.get("slug", ""))
        parts.append(t("msg_celebration_badge", lang, title=title, emoji=badge.get("emoji", "")))

    # Streak freeze
    if freeze_used:
        parts.append(t("msg_celebration_freeze", lang, n=freezes_left))

    return "\n".join(parts)


def breadcrumb(*parts: str) -> str:
    """Build a breadcrumb path like '⚙️ Settings › 🔔 Notifications'."""
    return " › ".join(parts)

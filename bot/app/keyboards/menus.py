"""Keyboards for the bot."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from app.translations import t


def ui_language_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """UI Language selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ui_lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="ui_lang_en"),
        ],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="settings_back")],
    ])


def poem_language_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Poetry language selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ],
        [InlineKeyboardButton(text="🌍 Both / Оба", callback_data="lang_both")],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="settings_back")],
    ])


def main_menu_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Persistent bottom menu — 3 rows, 7+ buttons."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_new", lang)), KeyboardButton(text=t("btn_review", lang))],
            [KeyboardButton(text=t("btn_profile", lang)), KeyboardButton(text=t("btn_favorites", lang)), KeyboardButton(text=t("btn_history", lang))],
            [KeyboardButton(text=t("btn_leaderboard_short", lang)), KeyboardButton(text=t("btn_settings", lang)), KeyboardButton(text=t("btn_help_short", lang))],
        ],
        resize_keyboard=True,
        persistent=True
    )


def new_poem_method_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Options for getting a new poem."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_surprise", lang), callback_data="new_surprise")],
        [InlineKeyboardButton(text=t("btn_mood", lang), callback_data="new_mood")],
        [InlineKeyboardButton(text=t("btn_collections", lang), callback_data="new_collections")],
        [InlineKeyboardButton(text=t("btn_url", lang), callback_data="new_url")],
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel")],
    ])


def cancel_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Generic cancel button for FSM states."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel")]
    ])


def poem_action_keyboard(poem_id: str, is_new: bool = True, lang: str = "ru", show_full: bool = False, is_favorite: bool = False) -> InlineKeyboardMarkup:
    """Action buttons after a poem is shown."""
    buttons = [
        [
            InlineKeyboardButton(text=t("btn_recite", lang), callback_data=f"recite_{poem_id}"),
            InlineKeyboardButton(text=t("btn_flashcard", lang), callback_data=f"learn_{poem_id}"),
        ],
        [
            InlineKeyboardButton(text=t("btn_stanza_mode", lang), callback_data=f"stanza_{poem_id}"),
            InlineKeyboardButton(text=t("btn_listen", lang), callback_data=f"tts_{poem_id}"),
        ],
    ]
    if is_favorite:
        buttons.append([InlineKeyboardButton(text=t("btn_fav_remove", lang), callback_data=f"fav_del_{poem_id}")])
    else:
        buttons.append([InlineKeyboardButton(text=t("btn_fav_add", lang), callback_data=f"fav_add_{poem_id}")])
    if show_full:
        buttons.append([InlineKeyboardButton(text=t("btn_show_full", lang), callback_data=f"show_poem_{poem_id}")])
    if is_new:
        buttons.append([InlineKeyboardButton(text=t("btn_skip", lang), callback_data=f"skip_{poem_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def review_score_keyboard(poem_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Score buttons for SM-2 review (0-5)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("score_0", lang), callback_data=f"score_{poem_id}_0"),
            InlineKeyboardButton(text=t("score_1", lang), callback_data=f"score_{poem_id}_1"),
            InlineKeyboardButton(text=t("score_2", lang), callback_data=f"score_{poem_id}_2"),
        ],
        [
            InlineKeyboardButton(text=t("score_3", lang), callback_data=f"score_{poem_id}_3"),
            InlineKeyboardButton(text=t("score_4", lang), callback_data=f"score_{poem_id}_4"),
            InlineKeyboardButton(text=t("score_5", lang), callback_data=f"score_{poem_id}_5"),
        ],
        [InlineKeyboardButton(text=t("btn_recite", lang), callback_data=f"recite_{poem_id}")],
    ])


def settings_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Settings menu."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_ui_lang", lang), callback_data="settings_ui_lang")],
        [InlineKeyboardButton(text=t("btn_poem_lang", lang), callback_data="settings_poem_lang")],
        [InlineKeyboardButton(text=t("btn_notif_time", lang), callback_data="settings_notif_time")],
        [InlineKeyboardButton(text=t("btn_notifications_toggle", lang), callback_data="settings_notif_toggle")],
        [InlineKeyboardButton(text=t("btn_length_pref", lang), callback_data="settings_length_pref")],
        [InlineKeyboardButton(text=t("btn_reset_progress", lang), callback_data="settings_reset")],
    ])


def notification_time_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Time picker for notifications."""
    times = ["08:00", "10:00", "12:00", "14:00", "18:00", "20:00", "22:00"]
    buttons = [
        [InlineKeyboardButton(text=f"🕐 {time}", callback_data=f"notif_{time.replace(':', '')}")]
        for time in times
    ]
    buttons.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="settings_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def post_review_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Navigation after a review result."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_more_review", lang), callback_data="menu_review"),
            InlineKeyboardButton(text=t("btn_main_menu", lang), callback_data="menu_main"),
        ],
    ])


def post_stanza_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Navigation after stanza mode completion."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_more_review", lang), callback_data="menu_review"),
            InlineKeyboardButton(text=t("btn_new_poem", lang), callback_data="new_surprise"),
        ],
        [InlineKeyboardButton(text=t("btn_main_menu", lang), callback_data="menu_main")],
    ])


def stanza_viewing_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Buttons while viewing a stanza (choose how to practice)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_stanza_recite", lang), callback_data="st_recite"),
            InlineKeyboardButton(text=t("btn_stanza_type", lang), callback_data="st_type"),
        ],
        [
            InlineKeyboardButton(text=t("btn_stanza_next", lang), callback_data="st_next"),
            InlineKeyboardButton(text=t("btn_stanza_know_all", lang), callback_data="st_know_all"),
        ],
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="st_back")],
    ])


def stanza_result_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Buttons after a failed stanza recitation attempt."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_stanza_retry", lang), callback_data="st_retry"),
            InlineKeyboardButton(text=t("btn_stanza_show", lang), callback_data="st_peek"),
        ],
        [InlineKeyboardButton(text=t("btn_stanza_next", lang), callback_data="st_next")],
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="st_back")],
    ])


def recite_prompt_keyboard(poem_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Prompt options while bot is waiting for a recitation (voice/text/hint)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_recite", lang), callback_data=f"recite_{poem_id}"),
            InlineKeyboardButton(text=t("btn_stanza_type", lang), callback_data=f"type_{poem_id}"),
        ],
        [InlineKeyboardButton(text=t("btn_hint", lang), callback_data=f"hint_{poem_id}")],
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel")],
    ])


def profile_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Profile sub-actions after the profile text."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_achievements", lang), callback_data="profile_achievements"),
            InlineKeyboardButton(text=t("btn_my_history", lang), callback_data="profile_history"),
        ],
        [
            InlineKeyboardButton(text=t("btn_my_favorites", lang), callback_data="profile_favorites"),
            InlineKeyboardButton(text=t("btn_my_stats", lang), callback_data="profile_stats"),
        ],
        [InlineKeyboardButton(text=t("btn_back_to_menu", lang), callback_data="menu_main")],
    ])


def length_pref_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Poem length preference picker."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_length_short", lang), callback_data="length_short"),
            InlineKeyboardButton(text=t("btn_length_medium", lang), callback_data="length_medium"),
        ],
        [
            InlineKeyboardButton(text=t("btn_length_long", lang), callback_data="length_long"),
            InlineKeyboardButton(text=t("btn_length_any", lang), callback_data="length_any"),
        ],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="settings_back")],
    ])


def reset_confirm_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Confirmation for resetting progress."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_reset_yes", lang), callback_data="reset_confirm_yes")],
        [InlineKeyboardButton(text=t("btn_reset_no", lang), callback_data="settings_back")],
    ])


def help_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Interactive help menu with topic buttons."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_help_learn", lang), callback_data="help_learn")],
        [InlineKeyboardButton(text=t("btn_help_voice", lang), callback_data="help_voice")],
        [InlineKeyboardButton(text=t("btn_help_xp", lang), callback_data="help_xp")],
        [InlineKeyboardButton(text=t("btn_help_contact", lang), callback_data="help_contact")],
    ])


def help_back_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Back button from help sub-screen."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_help_back", lang), callback_data="help_back")],
    ])


# ─── Poem Finder Flow Keyboards ─────────────────────────────

_FINDER_FOOTER_KEYS = [
    ("btn_finder_freetext", "finder_freetext"),
    ("btn_finder_skip", "finder_skip"),
    ("btn_cancel", "cancel"),
]


def _finder_footer(lang: str) -> list[list[InlineKeyboardButton]]:
    """Common bottom row for finder keyboards: Free text | Skip | Cancel."""
    return [
        [
            InlineKeyboardButton(text=t(k, lang), callback_data=v)
            for k, v in _FINDER_FOOTER_KEYS
        ]
    ]


def finder_mood_keyboard(lang: str, show_last: bool = False) -> InlineKeyboardMarkup:
    """Mood selection chips for the poem finder."""
    moods = [
        ("mood_sad", "finder_mood_sad"),
        ("mood_love", "finder_mood_love"),
        ("mood_inspirational", "finder_mood_inspirational"),
        ("mood_reflective", "finder_mood_reflective"),
        ("mood_joyful", "finder_mood_joyful"),
        ("mood_philosophical", "finder_mood_philosophical"),
        ("mood_nature", "finder_mood_nature"),
        ("mood_patriotic", "finder_mood_patriotic"),
    ]
    rows: list[list[InlineKeyboardButton]] = []
    if show_last:
        rows.append([InlineKeyboardButton(
            text=t("msg_finder_same_as_last", lang),
            callback_data="finder_same_as_last",
        )])
    # 2 chips per row
    for i in range(0, len(moods), 2):
        row = [
            InlineKeyboardButton(text=t(k, lang), callback_data=v)
            for k, v in moods[i:i + 2]
        ]
        rows.append(row)
    rows.extend(_finder_footer(lang))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finder_length_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Length selection chips for the poem finder."""
    chips = [
        ("length_short", "finder_length_short"),
        ("length_medium", "finder_length_medium"),
        ("length_long", "finder_length_long"),
        ("length_any", "finder_length_any"),
    ]
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(k, lang), callback_data=v) for k, v in chips[:2]],
        [InlineKeyboardButton(text=t(k, lang), callback_data=v) for k, v in chips[2:]],
    ]
    rows.extend(_finder_footer(lang))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finder_era_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Era selection chips for the poem finder."""
    chips = [
        ("era_classic", "finder_era_classic"),
        ("era_silver_age", "finder_era_silver_age"),
        ("era_soviet", "finder_era_soviet"),
        ("era_modern", "finder_era_modern"),
        ("era_any", "finder_era_any"),
    ]
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(k, lang), callback_data=v) for k, v in chips[:2]],
        [InlineKeyboardButton(text=t(k, lang), callback_data=v) for k, v in chips[2:4]],
        [InlineKeyboardButton(text=t(chips[4][0], lang), callback_data=chips[4][1])],
    ]
    rows.extend(_finder_footer(lang))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finder_author_keyboard(
    lang: str,
    authors: list[dict] | None = None,
) -> InlineKeyboardMarkup:
    """Author selection chips (top authors from DB) for the poem finder."""
    rows: list[list[InlineKeyboardButton]] = []
    if authors:
        for i in range(0, len(authors), 2):
            row = [
                InlineKeyboardButton(
                    text=f"👤 {a['author']}",
                    callback_data=f"finder_author_{a['author'][:40]}",
                )
                for a in authors[i:i + 2]
            ]
            rows.append(row)
    rows.append([
        InlineKeyboardButton(
            text=t("btn_finder_search_author", lang),
            callback_data="finder_freetext",
        ),
    ])
    rows.append([
        InlineKeyboardButton(text=t("length_any", lang), callback_data="finder_author_any"),
    ])
    rows.extend(_finder_footer(lang))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def finder_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Confirmation buttons for the poem finder."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_finder_find", lang), callback_data="finder_confirm"),
            InlineKeyboardButton(text=t("btn_finder_restart", lang), callback_data="finder_restart"),
        ],
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel")],
    ])


def finder_followup_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Follow-up keyboard after showing finder results."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_finder_different", lang), callback_data="new_mood"),
            InlineKeyboardButton(text=t("btn_finder_surprise", lang), callback_data="new_surprise"),
        ],
        [InlineKeyboardButton(text=t("btn_main_menu", lang), callback_data="menu_main")],
    ])


def freetext_followup_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Follow-up keyboard after a free-text chat search."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("btn_more_like_this", lang), callback_data="ft_more"),
            InlineKeyboardButton(text=t("btn_surprise_me", lang), callback_data="ft_random"),
        ],
        [InlineKeyboardButton(text=t("btn_refine_query", lang), callback_data="ft_refine")],
        [InlineKeyboardButton(text=t("btn_main_menu", lang), callback_data="menu_main")],
    ])


# ─── History Filter Keyboard ────────────────────────────────

def history_filter_keyboard(lang: str, active: str = "all") -> InlineKeyboardMarkup:
    """Filter chips for the history view."""
    filters = [
        ("btn_hist_filter_all", "hist_filter_all"),
        ("btn_hist_filter_learning", "hist_filter_learning"),
        ("btn_hist_filter_reviewing", "hist_filter_reviewing"),
        ("btn_hist_filter_memorized", "hist_filter_memorized"),
    ]
    chip_row = []
    for key, cb in filters:
        label = t(key, lang)
        status_val = cb.replace("hist_filter_", "")
        if status_val == active:
            label = f"[{label}]"
        chip_row.append(InlineKeyboardButton(text=label, callback_data=cb))
    return InlineKeyboardMarkup(inline_keyboard=[
        chip_row[:2],
        chip_row[2:],
        [InlineKeyboardButton(text=t("btn_main_menu", lang), callback_data="menu_main")],
    ])


# ─── Collections Keyboards ──────────────────────────────────

def collections_list_keyboard(collections: list[dict], lang: str) -> InlineKeyboardMarkup:
    """List of collection buttons."""
    title_key = "title_ru" if lang == "ru" else "title_en"
    rows: list[list[InlineKeyboardButton]] = []
    for col in collections:
        emoji = col.get("cover_emoji", "📚")
        title = col.get(title_key, col.get("slug", ""))
        count = col.get("poem_count", 0)
        rows.append([
            InlineKeyboardButton(
                text=f"{emoji} {title} ({count})",
                callback_data=f"col_{col['slug']}",
            )
        ])
    rows.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def collection_pagination_keyboard(slug: str, page: int, total_pages: int, lang: str) -> InlineKeyboardMarkup:
    """Pagination for poems inside a collection."""
    buttons: list[InlineKeyboardButton] = []
    if page > 0:
        buttons.append(InlineKeyboardButton(
            text=t("btn_prev_page", lang), callback_data=f"colpage_{slug}_{page - 1}",
        ))
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(
            text=t("btn_next_page", lang), callback_data=f"colpage_{slug}_{page + 1}",
        ))
    rows: list[list[InlineKeyboardButton]] = []
    if buttons:
        rows.append(buttons)
    rows.append([InlineKeyboardButton(text=t("btn_back", lang), callback_data="new_collections")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def favorites_pagination_keyboard(page: int, total_pages: int, lang: str) -> InlineKeyboardMarkup:
    """Pagination for favorites list."""
    buttons: list[InlineKeyboardButton] = []
    if page > 0:
        buttons.append(InlineKeyboardButton(
            text=t("btn_prev_page", lang), callback_data=f"favpage_{page - 1}",
        ))
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(
            text=t("btn_next_page", lang), callback_data=f"favpage_{page + 1}",
        ))
    rows: list[list[InlineKeyboardButton]] = []
    if buttons:
        rows.append(buttons)
    rows.append([InlineKeyboardButton(text=t("btn_main_menu", lang), callback_data="menu_main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


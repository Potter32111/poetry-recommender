"""Bot command and callback handlers."""

import io
import logging

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.api_client import api
from app.translations import t
from app.utils import (
    get_user_lang,
    format_poem_card,
    invalidate_lang_cache,
    split_stanzas,
    build_xp_bar,
    build_stanza_progress,
    compare_stanza_text,
    escape_md,
    breadcrumb,
)
from app.keyboards.menus import (
    ui_language_keyboard,
    poem_language_keyboard,
    main_menu_keyboard,
    new_poem_method_keyboard,
    poem_action_keyboard,
    review_score_keyboard,
    settings_keyboard,
    cancel_keyboard,
    notification_time_keyboard,
    post_review_keyboard,
    post_stanza_keyboard,
    stanza_viewing_keyboard,
    stanza_result_keyboard,
    profile_keyboard,
    length_pref_keyboard,
    reset_confirm_keyboard,
    help_keyboard,
    help_back_keyboard,
    finder_mood_keyboard,
    finder_length_keyboard,
    finder_era_keyboard,
    finder_author_keyboard,
    finder_confirm_keyboard,
    finder_followup_keyboard,
    history_filter_keyboard,
    collections_list_keyboard,
    collection_pagination_keyboard,
    favorites_pagination_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()

class RecommendFlow(StatesGroup):
    waiting_for_mood = State()
    waiting_for_url = State()


class StanzaFlow(StatesGroup):
    viewing_stanza = State()
    reciting_voice = State()
    reciting_text = State()


class FinderFlow(StatesGroup):
    picking_mood = State()
    picking_length = State()
    picking_era = State()
    picking_author = State()
    confirming = State()
    freetext_mood = State()
    freetext_length = State()
    freetext_era = State()
    freetext_author = State()


# ─── Global Cancel state ────────────────────────────────────
@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    await state.clear()
    lang = await get_user_lang(callback.from_user.id)
    try:
        await callback.message.edit_text(t("btn_cancel", lang))
    except Exception:
        pass
    await callback.message.answer(
        t("msg_whats_next", lang),
        reply_markup=main_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_main")
async def cb_menu_main(callback: CallbackQuery, state: FSMContext) -> None:
    """Return to main menu from post-action keyboards."""
    if not callback.from_user or not callback.message:
        return
    await state.clear()
    lang = await get_user_lang(callback.from_user.id)
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer(
        t("msg_welcome", lang),
        reply_markup=main_menu_keyboard(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


# ─── Commands ───────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start — register user or welcome back returning user."""
    user = message.from_user
    if not user:
        return

    try:
        user_data = await api.create_user(user.id, user.username, user.first_name)
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        user_data = {}

    if not user_data.get("_is_new", True):
        lang = await get_user_lang(user.id)
        name = user_data.get("first_name") or user.first_name or ""
        streak = user_data.get("streak", 0)
        try:
            due = await api.get_due_reviews(user.id)
            due_count = len(due)
        except Exception:
            due_count = 0
        await message.answer(
            t("msg_welcome_back", lang, name=name, due=due_count, streak=streak),
            reply_markup=main_menu_keyboard(lang),
            parse_mode="Markdown",
        )
        return

    await message.answer(
        "👋 Welcome to Poetry Companion! / Добро пожаловать!\n\n"
        "Please choose your interface language / Выберите язык интерфейса:",
        reply_markup=ui_language_keyboard(),
        parse_mode="Markdown",
    )


@router.message(Command("leaderboard"))
async def cmd_leaderboard(message: Message) -> None:
    """Handle /leaderboard — show the top 10 users."""
    if not message.from_user:
        return

    lang = await get_user_lang(message.from_user.id)

    try:
        users = await api.get_leaderboard()
    except Exception as e:
        logger.error(f"Failed to fetch leaderboard: {e}")
        await message.answer(t("msg_leaderboard_error", lang))
        return

    if not users:
        await message.answer(t("msg_leaderboard_empty", lang))
        return

    text = t("msg_leaderboard_title", lang) + "\n\n"
    for i, user in enumerate(users):
        rank = i + 1
        if rank == 1:
            emoji = "🥇"
        elif rank == 2:
            emoji = "🥈"
        elif rank == 3:
            emoji = "🥉"
        else:
            emoji = f"{rank}."
            
        name = user.get("first_name") or f"User {user.get('telegram_id')}"
        level = user.get("level", 1)
        xp = user.get("xp", 0)
        streak = user.get("streak", 0)
        
        text += t("msg_leaderboard_row", lang, emoji=emoji, name=name, level=level, xp=xp, streak=streak) + "\n"

    await message.answer(text, parse_mode="Markdown")


@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    """Handle /settings — show settings menu."""
    if not message.from_user:
        return
    lang = await get_user_lang(message.from_user.id)
    await message.answer(t("msg_settings", lang), reply_markup=settings_keyboard(lang))


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help — show interactive help menu."""
    if not message.from_user:
        return
    lang = await get_user_lang(message.from_user.id)
    await message.answer(t("msg_help_title", lang), reply_markup=help_keyboard(lang), parse_mode="Markdown")


@router.message(Command("review"))
async def cmd_review(message: Message) -> None:
    """Handle /review — show poems due for review."""
    if not message.from_user:
        return
    await _send_review(message, message.from_user.id)


@router.message(Command("recommend"))
async def cmd_recommend(message: Message) -> None:
    """Handle /recommend — get a new poem recommendation."""
    if not message.from_user:
        return
    await _send_recommendation(message, message.from_user.id, mood=None)


@router.message(Command("progress"))
async def cmd_progress(message: Message) -> None:
    """Handle /progress — show user stats."""
    if not message.from_user:
        return
    await _send_progress(message, message.from_user.id)


# ─── Reply Keyboard Handlers ────────────────────────────────

@router.message(lambda msg: msg.text in [t("btn_new", "ru"), t("btn_new", "en")])
async def handle_new_poem_menu(message: Message) -> None:
    """Handle 'Get New Poem' reply button."""
    if not message.from_user:
        return
    lang = await get_user_lang(message.from_user.id)
    await message.answer(
        t("msg_new_poem", lang),
        reply_markup=new_poem_method_keyboard(lang),
        parse_mode="Markdown"
    )

@router.message(lambda msg: msg.text in [t("btn_review", "ru"), t("btn_review", "en")])
async def handle_review_menu(message: Message) -> None:
    """Handle 'Review' reply button."""
    if not message.from_user:
        return
    await _send_review(message, message.from_user.id)

@router.message(lambda msg: msg.text in [t("btn_profile", "ru"), t("btn_profile", "en")])
async def handle_profile_menu(message: Message) -> None:
    """Handle 'Profile' reply button."""
    if not message.from_user:
        return
    await _send_progress(message, message.from_user.id)

@router.message(lambda msg: msg.text in [t("btn_settings", "ru"), t("btn_settings", "en")])
async def handle_settings_menu(message: Message) -> None:
    """Handle 'Settings' reply button."""
    if not message.from_user:
        return
    lang = await get_user_lang(message.from_user.id)
    await message.answer(
        t("msg_settings", lang),
        reply_markup=settings_keyboard(lang)
    )


@router.message(lambda msg: msg.text in [t("btn_favorites", "ru"), t("btn_favorites", "en")])
async def handle_favorites_menu(message: Message) -> None:
    """Handle 'Favorites' reply button."""
    if not message.from_user:
        return
    await _send_favorites(message, message.from_user.id)


@router.message(lambda msg: msg.text in [t("btn_history", "ru"), t("btn_history", "en")])
async def handle_history_menu(message: Message) -> None:
    """Handle 'History' reply button."""
    if not message.from_user:
        return
    await _send_history(message, message.from_user.id)


@router.message(lambda msg: msg.text in [t("btn_leaderboard_short", "ru"), t("btn_leaderboard_short", "en")])
async def handle_leaderboard_menu(message: Message) -> None:
    """Handle 'Leaderboard' reply button."""
    if not message.from_user:
        return
    await cmd_leaderboard(message)


@router.message(lambda msg: msg.text in [t("btn_help_short", "ru"), t("btn_help_short", "en")])
async def handle_help_menu(message: Message) -> None:
    """Handle 'Help' reply button."""
    if not message.from_user:
        return
    lang = await get_user_lang(message.from_user.id)
    await message.answer(t("msg_help_title", lang), reply_markup=help_keyboard(lang), parse_mode="Markdown")


# ─── Settings Flow Callbacks ──────────────────────────────

@router.callback_query(F.data.startswith("ui_lang_"))
async def cb_ui_language(callback: CallbackQuery) -> None:
    """Handle UI language selection (e.g. from /start)."""
    if not callback.data or not callback.from_user:
        return
    lang = callback.data.replace("ui_lang_", "")

    try:
        await api.update_user(callback.from_user.id, ui_language=lang)
    except Exception as e:
        logger.error(f"Failed to update UI language: {e}")

    invalidate_lang_cache(callback.from_user.id)

    await callback.message.delete()
    await callback.message.answer(
        t("btn_poem_lang", lang) + ":",
        reply_markup=poem_language_keyboard(lang),
        parse_mode="Markdown",
    )
    await callback.answer()

@router.callback_query(F.data.startswith("notif_"))
async def cb_notif_time(callback: CallbackQuery) -> None:
    """Handle notification time selection from time picker."""
    if not callback.data or not callback.from_user or not callback.message:
        return
    hhmm = callback.data.replace("notif_", "")
    formatted = f"{hhmm[:2]}:{hhmm[2:]}"
    lang = await get_user_lang(callback.from_user.id)
    try:
        await api.update_user(callback.from_user.id, notification_time=formatted)
        await callback.message.edit_text(
            t("msg_notif_saved", lang, time=formatted),
            reply_markup=settings_keyboard(lang),
        )
    except Exception as e:
        logger.error(f"Failed to save notification time: {e}")
        await callback.message.edit_text(
            t("msg_error_generic", lang), reply_markup=settings_keyboard(lang)
        )
    await callback.answer()

@router.callback_query(F.data == "settings_back")
async def cb_settings_back(callback: CallbackQuery) -> None:
    """Handle back button from settings sub-menus."""
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        t("msg_settings", lang), reply_markup=settings_keyboard(lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("settings_"))
async def cb_settings_actions(callback: CallbackQuery) -> None:
    if not callback.data or not callback.from_user:
        return
    action = callback.data.replace("settings_", "")
    lang = await get_user_lang(callback.from_user.id)
    
    if action == "ui_lang":
        bc = breadcrumb(t("msg_settings", lang).split("\n")[0], t("btn_ui_lang", lang))
        await callback.message.edit_text(
            bc + "\n\n" + t("btn_ui_lang", lang), reply_markup=ui_language_keyboard(lang)
        )
    elif action == "poem_lang":
        bc = breadcrumb(t("msg_settings", lang).split("\n")[0], t("btn_poem_lang", lang))
        await callback.message.edit_text(
            bc + "\n\n" + t("btn_poem_lang", lang), reply_markup=poem_language_keyboard(lang)
        )
    elif action == "notif_time":
        bc = breadcrumb(t("msg_settings", lang).split("\n")[0], t("btn_notif_time", lang))
        await callback.message.edit_text(
            bc + "\n\n" + t("btn_notif_time", lang), reply_markup=notification_time_keyboard(lang)
        )
    elif action == "notif_toggle":
        try:
            user = await api.get_user(callback.from_user.id)
            prefs = user.get("preferences", {}) or {}
            enabled = prefs.get("notifications_enabled", True)
            prefs["notifications_enabled"] = not enabled
            await api.update_user(callback.from_user.id, preferences=prefs)
            msg_key = "msg_notifications_off" if enabled else "msg_notifications_on"
            bc = breadcrumb(t("msg_settings", lang).split("\n")[0], t("btn_notifications_toggle", lang))
            await callback.message.edit_text(
                bc + "\n\n" + t(msg_key, lang), reply_markup=settings_keyboard(lang)
            )
        except Exception as e:
            logger.error(f"Failed to toggle notifications: {e}")
            await callback.message.answer(t("msg_error_generic", lang))
    elif action == "length_pref":
        bc = breadcrumb(t("msg_settings", lang).split("\n")[0], t("btn_length_pref", lang))
        await callback.message.edit_text(
            bc + "\n\n" + t("msg_length_pref_title", lang), reply_markup=length_pref_keyboard(lang)
        )
    elif action == "reset":
        bc = breadcrumb(t("msg_settings", lang).split("\n")[0], t("btn_reset_progress", lang))
        await callback.message.edit_text(
            bc + "\n\n" + t("msg_reset_confirm", lang), reply_markup=reset_confirm_keyboard(lang)
        )
    await callback.answer()

@router.callback_query(F.data.startswith("lang_"))
async def cb_poetry_language(callback: CallbackQuery) -> None:
    """Handle Poetry language selection."""
    if not callback.data or not callback.from_user:
        return
    lang_pref = callback.data.replace("lang_", "")

    try:
        user_before = await api.get_user(callback.from_user.id)
        is_settings_change = (
            user_before.get("xp", 0) > 0 or user_before.get("level", 1) > 1
        )
    except Exception:
        is_settings_change = False

    try:
        await api.update_user(callback.from_user.id, language_pref=lang_pref)
    except Exception as e:
        logger.error(f"Failed to update language: {e}")

    invalidate_lang_cache(callback.from_user.id)

    lang = await get_user_lang(callback.from_user.id)
    await callback.message.delete()
    if is_settings_change:
        await callback.message.answer(
            t("msg_saved", lang) + "\n" + t("msg_settings", lang),
            reply_markup=settings_keyboard(lang),
        )
    else:
        await callback.message.answer(
            t("msg_welcome", lang),
            reply_markup=main_menu_keyboard(lang),
            parse_mode="Markdown",
        )
    await callback.answer()


# ─── Length Preference Callbacks ──────────────────────────

@router.callback_query(F.data.startswith("length_"))
async def cb_length_pref(callback: CallbackQuery) -> None:
    """Handle poem length preference selection."""
    if not callback.data or not callback.from_user or not callback.message:
        return
    choice = callback.data.replace("length_", "")
    lang = await get_user_lang(callback.from_user.id)
    try:
        user = await api.get_user(callback.from_user.id)
        prefs = user.get("preferences", {}) or {}
        prefs["preferred_length"] = choice
        await api.update_user(callback.from_user.id, preferences=prefs)
        label = t(f"btn_length_{choice}", lang)
        await callback.message.edit_text(
            t("msg_length_saved", lang, choice=label), reply_markup=settings_keyboard(lang)
        )
    except Exception as e:
        logger.error(f"Failed to save length pref: {e}")
        await callback.message.answer(t("msg_error_generic", lang))
    await callback.answer()


# ─── Reset Progress Confirmation ─────────────────────────

@router.callback_query(F.data == "reset_confirm_yes")
async def cb_reset_confirm(callback: CallbackQuery) -> None:
    """Confirm and execute progress reset."""
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    try:
        await api.reset_progress(callback.from_user.id)
        await callback.message.edit_text(
            t("msg_reset_done", lang), reply_markup=settings_keyboard(lang)
        )
    except Exception as e:
        logger.error(f"Failed to reset progress: {e}")
        await callback.message.answer(t("msg_error_generic", lang))
    await callback.answer()


# ─── Profile Sub-Action Callbacks ────────────────────────

@router.callback_query(F.data == "profile_achievements")
async def cb_profile_achievements(callback: CallbackQuery) -> None:
    """Show achievements screen with unlocked/locked badges."""
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    bc = breadcrumb(t("btn_profile", lang), t("btn_achievements", lang))
    try:
        badges = await api.get_achievements(callback.from_user.id)
        lines = [bc, "", t("msg_achievements_title", lang), ""]
        for b in badges:
            title = b.get("title_ru" if lang == "ru" else "title_en", b.get("slug", ""))
            desc = b.get("description_ru" if lang == "ru" else "description_en", "")
            emoji = b.get("emoji", "")
            awarded = b.get("awarded_at")
            if awarded:
                date_str = awarded[:10]
                lines.append(t("msg_badge_unlocked_row", lang, emoji=emoji, title=title, description=desc, date=date_str))
            else:
                lines.append(t("msg_badge_locked", lang, title=f"{emoji} {title}"))
        await callback.message.edit_text(
            "\n".join(lines), reply_markup=profile_keyboard(lang), parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to load achievements: {e}")
        await callback.message.edit_text(
            bc + "\n\n" + t("msg_error_generic", lang), reply_markup=profile_keyboard(lang)
        )
    await callback.answer()


@router.callback_query(F.data == "profile_history")
async def cb_profile_history(callback: CallbackQuery) -> None:
    """Show history from profile screen."""
    if not callback.from_user or not callback.message:
        return
    await _send_history(callback.message, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "profile_favorites")
async def cb_profile_favorites(callback: CallbackQuery) -> None:
    """Show favorites from profile screen."""
    if not callback.from_user or not callback.message:
        return
    await _send_favorites(callback.message, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "profile_stats")
async def cb_profile_stats(callback: CallbackQuery) -> None:
    """Show stats with daily challenge and streak freeze info."""
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    bc = breadcrumb(t("btn_profile", lang), t("btn_my_stats", lang))
    try:
        user = await api.get_user(callback.from_user.id)
        challenge = await api.get_today_challenge(callback.from_user.id)

        from app.utils import _challenge_goal_text
        goal_text = _challenge_goal_text(
            challenge.get("goal_type", ""), challenge.get("goal_target", 1), lang
        )
        challenge_line = t(
            "msg_challenge_progress", lang,
            goal=goal_text,
            progress=challenge.get("current_progress", 0),
            target=challenge.get("goal_target", 1),
        )
        if challenge.get("completed_at"):
            challenge_line += " ✅"

        freeze_line = t("msg_freeze_count", lang, n=user.get("streak_freezes_available", 0))

        text = f"{bc}\n\n{t('msg_challenge_title', lang)}\n{challenge_line}\n\n{freeze_line}"
        await callback.message.edit_text(
            text, reply_markup=profile_keyboard(lang), parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to load stats: {e}")
        await callback.message.edit_text(
            bc + "\n\n" + t("msg_error_generic", lang), reply_markup=profile_keyboard(lang)
        )
    await callback.answer()


# ─── Help Sub-Screen Callbacks ───────────────────────────

@router.callback_query(F.data == "help_back")
async def cb_help_back(callback: CallbackQuery) -> None:
    """Return to help menu."""
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        t("msg_help_title", lang), reply_markup=help_keyboard(lang), parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("help_"))
async def cb_help_section(callback: CallbackQuery) -> None:
    """Show a help sub-section."""
    if not callback.data or not callback.from_user or not callback.message:
        return
    section = callback.data.replace("help_", "")
    lang = await get_user_lang(callback.from_user.id)

    key_map = {
        "learn": ("msg_help_learn", "btn_help_learn"),
        "voice": ("msg_help_voice", "btn_help_voice"),
        "xp": ("msg_help_xp", "btn_help_xp"),
        "contact": ("msg_help_contact", "btn_help_contact"),
    }
    msg_key, btn_key = key_map.get(section, ("msg_feature_wip", "btn_help_short"))
    bc = breadcrumb(t("btn_help_short", lang), t(btn_key, lang))
    await callback.message.edit_text(
        bc + "\n\n" + t(msg_key, lang), reply_markup=help_back_keyboard(lang), parse_mode="Markdown"
    )
    await callback.answer()


# ─── New Poem Flow Callbacks ──────────────────────────────

@router.callback_query(F.data == "new_surprise")
async def cb_new_surprise(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    try:
        await callback.message.edit_text(t("msg_analyzing", lang))
    except Exception:
        pass
    await _send_recommendation(callback.message, callback.from_user.id, mood=None)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data == "new_mood")
async def cb_new_mood(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    # Check if user has previous finder filters
    show_last = False
    try:
        user = await api.get_user(callback.from_user.id)
        prefs = user.get("preferences", {}) or {}
        show_last = bool(prefs.get("last_filters"))
    except Exception:
        pass
    await callback.message.edit_text(
        t("msg_finder_mood", lang),
        reply_markup=finder_mood_keyboard(lang, show_last=show_last),
    )
    await state.set_state(FinderFlow.picking_mood)
    await state.update_data(finder_mood=None, finder_length=None, finder_era=None, finder_author=None)
    await callback.answer()

@router.callback_query(F.data == "menu_review")
async def cb_menu_review(callback: CallbackQuery) -> None:
    """Handle 'Start Review' push notification button."""
    if not callback.from_user or not callback.message:
        return
    await _send_review(callback.message, callback.from_user.id)
    await callback.answer()

@router.callback_query(F.data == "new_url")
async def cb_new_url(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        t("msg_ask_url", lang),
        reply_markup=cancel_keyboard(lang)
    )
    await state.set_state(RecommendFlow.waiting_for_url)
    await callback.answer()

@router.message(RecommendFlow.waiting_for_mood, F.text)
async def handle_mood(message: Message, state: FSMContext) -> None:
    """Legacy mood handler — kept for backward compatibility."""
    if not message.from_user or not message.text:
        return
    await state.clear()
    lang = await get_user_lang(message.from_user.id)
    wait_msg = await message.answer(t("msg_analyzing", lang))
    await _send_recommendation(message, message.from_user.id, mood=message.text)
    try:
        await wait_msg.delete()
    except Exception:
        pass


# ─── Finder Flow: "Same as last time" ───────────────────────

@router.callback_query(FinderFlow.picking_mood, F.data == "finder_same_as_last")
async def cb_finder_same_as_last(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    try:
        user = await api.get_user(callback.from_user.id)
        prefs = user.get("preferences", {}) or {}
        last = prefs.get("last_filters", {})
    except Exception:
        last = {}
    if not last:
        await callback.answer()
        return
    await state.update_data(
        finder_mood=last.get("mood"),
        finder_length=last.get("length"),
        finder_era=last.get("era"),
        finder_author=last.get("author"),
    )
    await state.set_state(FinderFlow.confirming)
    summary = _build_finder_summary(last.get("mood"), last.get("length"), last.get("era"), last.get("author"), lang)
    await callback.message.edit_text(
        t("msg_finder_confirm", lang, summary=summary),
        reply_markup=finder_confirm_keyboard(lang),
    )
    await callback.answer()


# ─── Finder Flow: Mood step ─────────────────────────────────

@router.callback_query(FinderFlow.picking_mood, F.data.startswith("finder_mood_"))
async def cb_finder_mood(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    mood_val = callback.data.replace("finder_mood_", "")
    lang = await get_user_lang(callback.from_user.id)
    await state.update_data(finder_mood=mood_val)
    mood_label = t(f"mood_{mood_val}", lang)
    await callback.message.edit_text(
        t("msg_finder_length", lang, mood=mood_label),
        reply_markup=finder_length_keyboard(lang),
    )
    await state.set_state(FinderFlow.picking_length)
    await callback.answer()


# ─── Finder Flow: Length step ────────────────────────────────

@router.callback_query(FinderFlow.picking_length, F.data.startswith("finder_length_"))
async def cb_finder_length(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    length_val = callback.data.replace("finder_length_", "")
    lang = await get_user_lang(callback.from_user.id)
    await state.update_data(finder_length=length_val if length_val != "any" else None)
    length_label = t(f"length_{length_val}", lang)
    await callback.message.edit_text(
        t("msg_finder_era", lang, length=length_label),
        reply_markup=finder_era_keyboard(lang),
    )
    await state.set_state(FinderFlow.picking_era)
    await callback.answer()


# ─── Finder Flow: Era step ──────────────────────────────────

@router.callback_query(FinderFlow.picking_era, F.data.startswith("finder_era_"))
async def cb_finder_era(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    era_val = callback.data.replace("finder_era_", "")
    lang = await get_user_lang(callback.from_user.id)
    await state.update_data(finder_era=era_val if era_val != "any" else None)
    era_label = t(f"era_{era_val}", lang)
    # Fetch top authors for the author keyboard
    try:
        authors = await api.get_top_authors(limit=6)
    except Exception:
        authors = []
    await callback.message.edit_text(
        t("msg_finder_author", lang, era=era_label),
        reply_markup=finder_author_keyboard(lang, authors=authors),
    )
    await state.set_state(FinderFlow.picking_author)
    await callback.answer()


# ─── Finder Flow: Author step ───────────────────────────────

@router.callback_query(FinderFlow.picking_author, F.data.startswith("finder_author_"))
async def cb_finder_author(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    author_val = callback.data.replace("finder_author_", "")
    lang = await get_user_lang(callback.from_user.id)
    await state.update_data(finder_author=author_val if author_val != "any" else None)
    await state.set_state(FinderFlow.confirming)
    data = await state.get_data()
    summary = _build_finder_summary(
        data.get("finder_mood"), data.get("finder_length"),
        data.get("finder_era"), data.get("finder_author"), lang,
    )
    await callback.message.edit_text(
        t("msg_finder_confirm", lang, summary=summary),
        reply_markup=finder_confirm_keyboard(lang),
    )
    await callback.answer()


# ─── Finder Flow: Skip for any step ─────────────────────────

@router.callback_query(FinderFlow.picking_mood, F.data == "finder_skip")
async def cb_finder_skip_mood(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await state.update_data(finder_mood=None)
    await callback.message.edit_text(
        t("msg_finder_length", lang, mood="—"),
        reply_markup=finder_length_keyboard(lang),
    )
    await state.set_state(FinderFlow.picking_length)
    await callback.answer()


@router.callback_query(FinderFlow.picking_length, F.data == "finder_skip")
async def cb_finder_skip_length(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await state.update_data(finder_length=None)
    await callback.message.edit_text(
        t("msg_finder_era", lang, length="—"),
        reply_markup=finder_era_keyboard(lang),
    )
    await state.set_state(FinderFlow.picking_era)
    await callback.answer()


@router.callback_query(FinderFlow.picking_era, F.data == "finder_skip")
async def cb_finder_skip_era(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await state.update_data(finder_era=None)
    try:
        authors = await api.get_top_authors(limit=6)
    except Exception:
        authors = []
    await callback.message.edit_text(
        t("msg_finder_author", lang, era="—"),
        reply_markup=finder_author_keyboard(lang, authors=authors),
    )
    await state.set_state(FinderFlow.picking_author)
    await callback.answer()


@router.callback_query(FinderFlow.picking_author, F.data == "finder_skip")
async def cb_finder_skip_author(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await state.update_data(finder_author=None)
    await state.set_state(FinderFlow.confirming)
    data = await state.get_data()
    summary = _build_finder_summary(
        data.get("finder_mood"), data.get("finder_length"),
        data.get("finder_era"), data.get("finder_author"), lang,
    )
    await callback.message.edit_text(
        t("msg_finder_confirm", lang, summary=summary),
        reply_markup=finder_confirm_keyboard(lang),
    )
    await callback.answer()


# ─── Finder Flow: Free text entry ───────────────────────────

@router.callback_query(FinderFlow.picking_mood, F.data == "finder_freetext")
async def cb_finder_freetext_mood(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        t("msg_finder_freetext", lang), reply_markup=cancel_keyboard(lang),
    )
    await state.set_state(FinderFlow.freetext_mood)
    await callback.answer()


@router.message(FinderFlow.freetext_mood, F.text)
async def handle_finder_freetext_mood(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return
    lang = await get_user_lang(message.from_user.id)
    await state.update_data(finder_mood=message.text)
    await message.answer(
        t("msg_finder_length", lang, mood=escape_md(message.text)),
        reply_markup=finder_length_keyboard(lang),
    )
    await state.set_state(FinderFlow.picking_length)


@router.callback_query(FinderFlow.picking_length, F.data == "finder_freetext")
async def cb_finder_freetext_length(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        t("msg_finder_freetext", lang), reply_markup=cancel_keyboard(lang),
    )
    await state.set_state(FinderFlow.freetext_length)
    await callback.answer()


@router.message(FinderFlow.freetext_length, F.text)
async def handle_finder_freetext_length(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return
    lang = await get_user_lang(message.from_user.id)
    await state.update_data(finder_length=message.text)
    await message.answer(
        t("msg_finder_era", lang, length=escape_md(message.text)),
        reply_markup=finder_era_keyboard(lang),
    )
    await state.set_state(FinderFlow.picking_era)


@router.callback_query(FinderFlow.picking_era, F.data == "finder_freetext")
async def cb_finder_freetext_era(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        t("msg_finder_freetext", lang), reply_markup=cancel_keyboard(lang),
    )
    await state.set_state(FinderFlow.freetext_era)
    await callback.answer()


@router.message(FinderFlow.freetext_era, F.text)
async def handle_finder_freetext_era(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return
    lang = await get_user_lang(message.from_user.id)
    await state.update_data(finder_era=message.text)
    try:
        authors = await api.get_top_authors(limit=6)
    except Exception:
        authors = []
    await message.answer(
        t("msg_finder_author", lang, era=escape_md(message.text)),
        reply_markup=finder_author_keyboard(lang, authors=authors),
    )
    await state.set_state(FinderFlow.picking_author)


@router.callback_query(FinderFlow.picking_author, F.data == "finder_freetext")
async def cb_finder_freetext_author(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        t("msg_finder_freetext", lang), reply_markup=cancel_keyboard(lang),
    )
    await state.set_state(FinderFlow.freetext_author)
    await callback.answer()


@router.message(FinderFlow.freetext_author, F.text)
async def handle_finder_freetext_author(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return
    lang = await get_user_lang(message.from_user.id)
    await state.update_data(finder_author=message.text)
    await state.set_state(FinderFlow.confirming)
    data = await state.get_data()
    summary = _build_finder_summary(
        data.get("finder_mood"), data.get("finder_length"),
        data.get("finder_era"), data.get("finder_author"), lang,
    )
    await message.answer(
        t("msg_finder_confirm", lang, summary=summary),
        reply_markup=finder_confirm_keyboard(lang),
    )


# ─── Finder Flow: Confirm / Restart ─────────────────────────

@router.callback_query(FinderFlow.confirming, F.data == "finder_confirm")
async def cb_finder_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    data = await state.get_data()
    mood = data.get("finder_mood")
    length = data.get("finder_length")
    era = data.get("finder_era")
    author = data.get("finder_author")
    await state.clear()

    await callback.message.edit_text(t("msg_analyzing", lang))

    # Save filters for "same as last time"
    try:
        user = await api.get_user(callback.from_user.id)
        prefs = user.get("preferences", {}) or {}
        prefs["last_filters"] = {"mood": mood, "length": length, "era": era, "author": author}
        await api.update_user(callback.from_user.id, preferences=prefs)
    except Exception as e:
        logger.error(f"Failed to save finder filters: {e}")

    # Fetch 3 results
    await _send_finder_results(callback.message, callback.from_user.id, mood, length, era, author, lang)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()


@router.callback_query(FinderFlow.confirming, F.data == "finder_restart")
async def cb_finder_restart(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    show_last = False
    try:
        user = await api.get_user(callback.from_user.id)
        prefs = user.get("preferences", {}) or {}
        show_last = bool(prefs.get("last_filters"))
    except Exception:
        pass
    await state.update_data(finder_mood=None, finder_length=None, finder_era=None, finder_author=None)
    await callback.message.edit_text(
        t("msg_finder_mood", lang),
        reply_markup=finder_mood_keyboard(lang, show_last=show_last),
    )
    await state.set_state(FinderFlow.picking_mood)
    await callback.answer()

@router.message(RecommendFlow.waiting_for_url, F.text)
async def handle_url(message: Message, state: FSMContext) -> None:
    if not message.from_user or not message.text:
        return
    await state.clear()
    lang = await get_user_lang(message.from_user.id)
    wait_msg = await message.answer(t("msg_analyzing", lang))
    
    try:
        poem = await api.parse_poem(message.text)
        await wait_msg.delete()
        await message.answer(
            format_poem_card(poem),
            reply_markup=poem_action_keyboard(poem["id"], is_new=True, lang=lang),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Parse command failed: {e}")
        await wait_msg.edit_text(t("msg_not_found", lang))


# ─── Poem Action Callbacks ──────────────────────────────────

@router.callback_query(F.data.startswith("learn_"))
async def cb_learn(callback: CallbackQuery) -> None:
    """Handle 'Self Check' — show review score options."""
    if not callback.data or not callback.from_user or not callback.message:
        return
    poem_id = callback.data.replace("learn_", "")
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.answer(
        t("msg_flashcard_prompt", lang),
        reply_markup=review_score_keyboard(poem_id, lang),
    )
    await callback.answer()

@router.callback_query(F.data.startswith("score_"))
async def cb_score(callback: CallbackQuery) -> None:
    """Handle SM-2 review score submission."""
    if not callback.data or not callback.from_user or not callback.message:
        return
    parts = callback.data.split("_")
    poem_id = parts[1]
    score = int(parts[2])
    
    lang = await get_user_lang(callback.from_user.id)

    # Note: We need to check previous XP level to show Level Up
    user_before = await api.get_user(callback.from_user.id)
    level_before = user_before.get("level", 1)

    try:
        result = await api.review_poem(callback.from_user.id, poem_id, score)
        
        # Check level up
        user_after = await api.get_user(callback.from_user.id)
        level_after = user_after.get("level", 1)
        
        level_up = level_after if level_after > level_before else None

        # Build celebration message
        from app.utils import format_celebration
        celebration = format_celebration(
            xp=15,
            level_up=level_up,
            challenge_progress=None,
            new_badges=[],
            freeze_used=False,
            freezes_left=user_after.get("streak_freezes_available", 0),
            lang=lang,
        )

        status_emoji = {
            "learning": "📖", "reviewing": "🔄", "memorized": "🌟"
        }.get(result.get("status", ""), "📚")

        # Encouragement based on score
        if score == 5:
            encourage = t("msg_encourage_perfect", lang)
        elif score >= 3:
            encourage = t("msg_encourage_good", lang)
        else:
            encourage = t("msg_encourage_low", lang)

        await callback.message.edit_text(
            f"{status_emoji} {celebration}\n{encourage}",
            reply_markup=post_review_keyboard(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Review failed: {e}")
        await callback.message.answer(t("msg_error_review", lang))

    await callback.answer()

@router.callback_query(F.data.startswith("skip_"))
async def cb_skip(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.data or not callback.from_user or not callback.message:
        return
    poem_id = callback.data.replace("skip_", "", 1)
    lang = await get_user_lang(callback.from_user.id)
    try:
        await api.skip_poem(callback.from_user.id, poem_id)
    except Exception as e:
        logger.error(f"Skip poem failed: {e}")
    try:
        await callback.message.edit_text(t("msg_analyzing", lang))
    except Exception:
        pass
    await _send_recommendation(callback.message, callback.from_user.id, mood=None, length=None)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()


# ─── Favorites Callbacks ─────────────────────────────────────

@router.callback_query(F.data.startswith("fav_add_"))
async def cb_fav_add(callback: CallbackQuery) -> None:
    """Add a poem to favorites."""
    if not callback.from_user or not callback.message or not callback.data:
        return
    poem_id = callback.data.replace("fav_add_", "", 1)
    lang = await get_user_lang(callback.from_user.id)
    try:
        await api.add_favorite(callback.from_user.id, poem_id)
        # Update keyboard to show remove button
        if callback.message.reply_markup:
            new_kb = poem_action_keyboard(poem_id, is_new=False, lang=lang, is_favorite=True)
            try:
                await callback.message.edit_reply_markup(reply_markup=new_kb)
            except Exception:
                pass
        await callback.answer(t("msg_fav_added", lang), show_alert=False)
    except Exception as e:
        logger.error(f"Failed to add favorite: {e}")
        await callback.answer(t("msg_error_generic", lang), show_alert=True)


@router.callback_query(F.data.startswith("fav_del_"))
async def cb_fav_del(callback: CallbackQuery) -> None:
    """Remove a poem from favorites."""
    if not callback.from_user or not callback.message or not callback.data:
        return
    poem_id = callback.data.replace("fav_del_", "", 1)
    lang = await get_user_lang(callback.from_user.id)
    try:
        await api.remove_favorite(callback.from_user.id, poem_id)
        # Update keyboard to show add button
        if callback.message.reply_markup:
            new_kb = poem_action_keyboard(poem_id, is_new=False, lang=lang, is_favorite=False)
            try:
                await callback.message.edit_reply_markup(reply_markup=new_kb)
            except Exception:
                pass
        await callback.answer(t("msg_fav_removed", lang), show_alert=False)
    except Exception as e:
        logger.error(f"Failed to remove favorite: {e}")
        await callback.answer(t("msg_error_generic", lang), show_alert=True)


@router.callback_query(F.data.startswith("favpage_"))
async def cb_fav_page(callback: CallbackQuery) -> None:
    """Handle favorites pagination."""
    if not callback.from_user or not callback.message or not callback.data:
        return
    page = int(callback.data.replace("favpage_", ""))
    await _send_favorites(callback.message, callback.from_user.id, page=page)
    await callback.answer()


# ─── History Filter Callbacks ────────────────────────────────

@router.callback_query(F.data.startswith("hist_filter_"))
async def cb_hist_filter(callback: CallbackQuery) -> None:
    """Handle history filter chip clicks."""
    if not callback.from_user or not callback.message or not callback.data:
        return
    filter_val = callback.data.replace("hist_filter_", "")
    status_filter = None if filter_val == "all" else filter_val
    await _send_history(callback.message, callback.from_user.id, status_filter=status_filter)
    await callback.answer()


# ─── Collections Callbacks ───────────────────────────────────

@router.callback_query(F.data == "new_collections")
async def cb_new_collections(callback: CallbackQuery) -> None:
    """Show list of curated collections."""
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    try:
        collections = await api.list_collections()
        if not collections:
            await callback.message.answer(t("msg_not_found", lang))
            await callback.answer()
            return
        await callback.message.answer(
            t("msg_collections_title", lang),
            reply_markup=collections_list_keyboard(collections, lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Failed to load collections: {e}")
        await callback.message.answer(t("msg_error_generic", lang))
    await callback.answer()


@router.callback_query(F.data.startswith("col_"))
async def cb_collection_view(callback: CallbackQuery) -> None:
    """Show poems in a collection (page 0)."""
    if not callback.from_user or not callback.message or not callback.data:
        return
    slug = callback.data.replace("col_", "", 1)
    await _send_collection_page(callback.message, callback.from_user.id, slug, 0)
    await callback.answer()


@router.callback_query(F.data.startswith("colpage_"))
async def cb_collection_page(callback: CallbackQuery) -> None:
    """Handle collection pagination."""
    if not callback.from_user or not callback.message or not callback.data:
        return
    parts = callback.data.replace("colpage_", "").rsplit("_", 1)
    if len(parts) != 2:
        await callback.answer()
        return
    slug, page_str = parts
    await _send_collection_page(callback.message, callback.from_user.id, slug, int(page_str))
    await callback.answer()


# ─── Stanza-by-Stanza Learning Mode ─────────────────────────

@router.callback_query(F.data.startswith("stanza_"))
async def cb_stanza_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Enter stanza-by-stanza learning mode for a poem."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    poem_id = callback.data.replace("stanza_", "")
    lang = await get_user_lang(callback.from_user.id)

    try:
        poem = await api.get_poem(poem_id)
    except Exception as e:
        logger.error(f"Failed to load poem for stanza mode: {e}")
        await callback.message.answer(t("msg_voice_load_error", lang))
        await callback.answer()
        return

    stanzas = split_stanzas(poem.get("text", ""))
    if len(stanzas) <= 1:
        await callback.message.answer(t("msg_stanza_single", lang))
        await callback.answer()
        return

    await state.set_state(StanzaFlow.viewing_stanza)
    await state.update_data(
        poem_id=poem_id,
        stanzas=stanzas,
        current_stanza_idx=0,
        completed_stanzas=[],
    )
    await _send_stanza_view(callback.message, stanzas, 0, set(), lang, edit=True)
    await callback.answer()


@router.callback_query(StanzaFlow.viewing_stanza, F.data == "st_recite")
async def cb_stanza_recite(callback: CallbackQuery, state: FSMContext) -> None:
    """Enter voice recitation for the current stanza."""
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await state.set_state(StanzaFlow.reciting_voice)
    await callback.message.answer(t("msg_stanza_recite_prompt", lang), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(StanzaFlow.viewing_stanza, F.data == "st_type")
async def cb_stanza_type(callback: CallbackQuery, state: FSMContext) -> None:
    """Enter text recitation for the current stanza."""
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await state.set_state(StanzaFlow.reciting_text)
    await callback.message.answer(t("msg_stanza_type_prompt", lang), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(StanzaFlow.viewing_stanza, F.data == "st_next")
async def cb_stanza_next(callback: CallbackQuery, state: FSMContext) -> None:
    """Skip to the next stanza."""
    if not callback.from_user or not callback.message:
        return
    await _advance_stanza(callback, state)
    await callback.answer()


@router.callback_query(StanzaFlow.viewing_stanza, F.data == "st_know_all")
async def cb_stanza_know_all(callback: CallbackQuery, state: FSMContext) -> None:
    """Mark all remaining stanzas as known and finish."""
    if not callback.from_user or not callback.message:
        return
    data = await state.get_data()
    stanzas = data.get("stanzas", [])
    completed = set(data.get("completed_stanzas", []))
    completed = set(range(len(stanzas)))
    await state.update_data(completed_stanzas=list(completed))
    await _finish_stanza_mode(callback.message, state, callback.from_user.id)
    await callback.answer()


@router.callback_query(StanzaFlow.viewing_stanza, F.data == "st_peek")
async def cb_stanza_peek_from_view(callback: CallbackQuery, state: FSMContext) -> None:
    """Show stanza text while viewing (after retry)."""
    if not callback.from_user or not callback.message:
        return
    await _peek_stanza(callback, state)
    await callback.answer()


@router.callback_query(StanzaFlow.viewing_stanza, F.data == "st_retry")
async def cb_stanza_retry_from_view(callback: CallbackQuery, state: FSMContext) -> None:
    """Retry from viewing state (re-show stanza with action buttons)."""
    if not callback.from_user or not callback.message:
        return
    data = await state.get_data()
    lang = await get_user_lang(callback.from_user.id)
    stanzas = data.get("stanzas", [])
    idx = data.get("current_stanza_idx", 0)
    completed = set(data.get("completed_stanzas", []))
    await _send_stanza_view(callback.message, stanzas, idx, completed, lang, edit=True)
    await callback.answer()


@router.callback_query(StanzaFlow.viewing_stanza, F.data == "st_back")
async def cb_stanza_back(callback: CallbackQuery, state: FSMContext) -> None:
    """Exit stanza mode."""
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    data = await state.get_data()
    poem_id = data.get("poem_id", "")
    await state.clear()
    await callback.message.edit_text(
        t("btn_cancel", lang),
        reply_markup=poem_action_keyboard(poem_id, is_new=False, lang=lang),
    )
    await callback.answer()


# ─── Stanza: Voice message handler ──────────────────────────

@router.message(StanzaFlow.reciting_voice, F.voice)
async def handle_stanza_voice(message: Message, state: FSMContext, bot: Bot) -> None:
    """Process voice message for stanza recitation."""
    if not message.from_user or not message.voice:
        return

    lang = await get_user_lang(message.from_user.id)
    data = await state.get_data()
    stanzas = data.get("stanzas", [])
    idx = data.get("current_stanza_idx", 0)

    if idx >= len(stanzas):
        await state.clear()
        return

    processing_msg = await message.answer(t("msg_processing", lang))

    try:
        voice_file = await bot.get_file(message.voice.file_id)
        voice_bytes = io.BytesIO()
        await bot.download_file(voice_file.file_path, voice_bytes)
        audio_data = voice_bytes.getvalue()

        # Transcribe only — no SM-2 update for stanza mode
        result = await api.transcribe(message.from_user.id, audio_data)
        transcribed = result.get("text", "")
        stanza_text = stanzas[idx]
        accuracy = compare_stanza_text(stanza_text, transcribed)
    except Exception as e:
        logger.error(f"Stanza voice check failed: {e}")
        try:
            await processing_msg.delete()
        except Exception:
            pass
        await message.answer(t("msg_voice_error", lang))
        await state.set_state(StanzaFlow.viewing_stanza)
        return

    try:
        await processing_msg.delete()
    except Exception:
        pass

    await _handle_stanza_result(message, state, accuracy, lang)


@router.message(StanzaFlow.reciting_voice)
async def handle_stanza_not_voice(message: Message, state: FSMContext) -> None:
    """Handle non-voice when expecting voice for stanza."""
    lang = await get_user_lang(message.from_user.id) if message.from_user else "ru"
    await message.answer(t("msg_voice_not_text", lang), parse_mode="Markdown")


# ─── Stanza: Text message handler ───────────────────────────

@router.message(StanzaFlow.reciting_text, F.text)
async def handle_stanza_text(message: Message, state: FSMContext) -> None:
    """Process typed text for stanza recitation."""
    if not message.from_user or not message.text:
        return

    lang = await get_user_lang(message.from_user.id)
    data = await state.get_data()
    stanzas = data.get("stanzas", [])
    idx = data.get("current_stanza_idx", 0)

    if idx >= len(stanzas):
        await state.clear()
        return

    accuracy = compare_stanza_text(stanzas[idx], message.text)
    await _handle_stanza_result(message, state, accuracy, lang)


# ─── Voice Without Context ───────────────────────────────
@router.message(F.voice)
async def handle_voice_no_context(message: Message) -> None:
    """Suggest using the Recite button when voice is sent without FSM context."""
    if not message.from_user:
        return
    lang = await get_user_lang(message.from_user.id)
    await message.answer(t("msg_voice_no_context", lang))


# ─── Unknown Message Handler (registered LAST) ───────────────
@router.message()
async def handle_unknown(message: Message, state: FSMContext) -> None:
    """Handle unrecognized messages with helpful suggestions."""
    if not message.from_user:
        return
    lang = await get_user_lang(message.from_user.id)

    if message.text:
        # Poem-like text: multiple lines
        if "\n" in message.text and message.text.count("\n") >= 2:
            await message.answer(t("msg_unknown_poem", lang))
            return
        # Question
        if "?" in message.text:
            await message.answer(t("msg_unknown_question", lang))
            return

    # Default fallback
    await message.answer(
        t("msg_unknown_default", lang),
        reply_markup=main_menu_keyboard(lang),
    )


# ─── Helpers ────────────────────────────────────────────────


def _build_reason_text(reason_key: str, reason_args: dict, lang: str) -> str:
    """Build human-readable recommendation reason from backend data."""
    if reason_key == "mood":
        return t("msg_rec_reason_mood", lang, mood=reason_args.get("mood", ""))
    if reason_key == "time":
        season = t(f"season_{reason_args.get('season', 'spring')}", lang)
        tod = t(f"time_{reason_args.get('time_of_day', 'evening')}", lang)
        return t("msg_rec_reason_time", lang, season=season, time_of_day=tod)
    if reason_key == "author":
        return t("msg_rec_reason_author", lang, author=reason_args.get("author", ""))
    return t("msg_rec_reason_discover", lang)


async def _send_recommendation(message: Message, telegram_id: int, mood: str | None = None, length: str | None = None) -> None:
    """Fetch and send a smart poem recommendation."""
    lang = await get_user_lang(telegram_id)
    try:
        recs = await api.get_pgvector_recommendations(telegram_id, mood=mood, length=length, limit=1)
        if not recs:
            raise ValueError("No recommendations returned")
            
        rec_poem = recs[0]
        poem_id = rec_poem["id"]
        poem_full = await api.get_poem(poem_id)

        card = format_poem_card(poem_full)
        reason_text = _build_reason_text(
            rec_poem.get("reason_key", "discover"),
            rec_poem.get("reason_args", {}),
            lang,
        )
        if reason_text:
            card += f"\n_✨ {escape_md(reason_text)}_"

        await message.answer(
            card,
            reply_markup=poem_action_keyboard(poem_id, is_new=True, lang=lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        await message.answer(t("msg_not_found", lang))


async def _send_recommendation_card(message: Message, rec_poem: dict, lang: str) -> None:
    """Render a single poem recommendation card."""
    poem_id = rec_poem["id"]
    try:
        poem_full = await api.get_poem(poem_id)
    except Exception as e:
        logger.error(f"Failed to load poem {poem_id}: {e}")
        return
    card = format_poem_card(poem_full)
    reason_text = _build_reason_text(
        rec_poem.get("reason_key", "discover"),
        rec_poem.get("reason_args", {}),
        lang,
    )
    if reason_text:
        card += f"\n_✨ {escape_md(reason_text)}_"
    await message.answer(
        card,
        reply_markup=poem_action_keyboard(poem_id, is_new=True, lang=lang),
        parse_mode="Markdown",
    )


def _build_finder_summary(
    mood: str | None, length: str | None, era: str | None, author: str | None, lang: str,
) -> str:
    """Build a human-readable summary of finder filter selections."""
    parts: list[str] = []
    if mood:
        label = t(f"mood_{mood}", lang) if not any(c in mood for c in " \t") else mood
        parts.append(label)
    if length:
        label = t(f"length_{length}", lang) if not any(c in length for c in " \t") else length
        parts.append(label)
    if era:
        label = t(f"era_{era}", lang) if not any(c in era for c in " \t") else era
        parts.append(label)
    if author:
        parts.append(f"👤 {author}")
    return " · ".join(parts) if parts else "🎲"


async def _send_finder_results(
    message: Message,
    telegram_id: int,
    mood: str | None,
    length: str | None,
    era: str | None,
    author: str | None,
    lang: str,
) -> None:
    """Fetch and send 3 finder results with follow-up keyboard."""
    try:
        recs = await api.get_pgvector_recommendations(
            telegram_id, mood=mood, length=length, era=era, author=author, limit=3,
        )
        if not recs:
            await message.answer(t("msg_finder_no_results", lang))
            return
        for rec_poem in recs:
            await _send_recommendation_card(message, rec_poem, lang)
        await message.answer(
            t("msg_finder_more", lang),
            reply_markup=finder_followup_keyboard(lang),
        )
    except Exception as e:
        logger.error(f"Finder results failed: {e}")
        await message.answer(t("msg_finder_no_results", lang))


async def _send_review(message: Message, telegram_id: int) -> None:
    """Show poems that are due for review."""
    lang = await get_user_lang(telegram_id)
    try:
        due = await api.get_due_reviews(telegram_id)
        if not due:
            await message.answer(
                t("msg_no_due_friendly", lang, btn_new=t("btn_new", lang)),
                reply_markup=main_menu_keyboard(lang),
            )
            return

        for mem in due[:3]:
            poem = await api.get_poem(mem["poem_id"])
            await message.answer(
                format_poem_card(poem, max_len=500),
                reply_markup=poem_action_keyboard(poem["id"], is_new=False, lang=lang),
                parse_mode="Markdown",
            )
    except Exception as e:
        logger.error(f"Review fetch failed: {e}")
        await message.answer(t("msg_error_generic", lang))


async def _send_progress(message: Message, telegram_id: int) -> None:
    """Show user's profile card with sub-action buttons."""
    lang = await get_user_lang(telegram_id)
    try:
        user = await api.get_user(telegram_id)
        stats = await api.get_progress(telegram_id)
        
        next_obj = user.get("level", 1) * 100
        xp_bar = build_xp_bar(user.get("xp", 0), next_obj)
        
        profile_text = t(
            "msg_profile", 
            lang,
            level=user.get("level", 1),
            xp=user.get("xp", 0),
            next_level_xp=next_obj,
            xp_bar=xp_bar,
            streak=user.get("streak", 0),
            learning=stats.get('learning', 0),
            reviewing=stats.get('reviewing', 0),
            memorized=stats.get('memorized', 0),
            total=stats.get('total', 0),
            due=stats.get('due_for_review', 0)
        )

        # Add streak freeze info
        freeze_count = user.get("streak_freezes_available", 0)
        profile_text += "\n" + t("msg_freeze_count", lang, n=freeze_count)

        # Add today's challenge
        try:
            challenge = await api.get_today_challenge(telegram_id)
            from app.utils import _challenge_goal_text
            goal_text = _challenge_goal_text(
                challenge.get("goal_type", ""), challenge.get("goal_target", 1), lang
            )
            challenge_line = t(
                "msg_challenge_progress", lang,
                goal=goal_text,
                progress=challenge.get("current_progress", 0),
                target=challenge.get("goal_target", 1),
            )
            if challenge.get("completed_at"):
                challenge_line += " ✅"
            profile_text += "\n\n" + t("msg_challenge_title", lang) + "\n" + challenge_line
        except Exception:
            pass

        await message.answer(
            profile_text,
            reply_markup=profile_keyboard(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Progress fetch failed: {e}")
        await message.answer(t("msg_error_generic", lang))


async def _send_favorites(message: Message, telegram_id: int, page: int = 0) -> None:
    """Show user's favorite poems with pagination."""
    lang = await get_user_lang(telegram_id)
    try:
        poems = await api.list_favorites(telegram_id)
    except Exception as e:
        logger.error(f"Failed to load favorites: {e}")
        await message.answer(t("msg_error_generic", lang))
        return

    if not poems:
        await message.answer(t("msg_fav_empty", lang), reply_markup=main_menu_keyboard(lang))
        return

    per_page = 5
    total_pages = max(1, (len(poems) + per_page - 1) // per_page)
    page = min(page, total_pages - 1)
    page_poems = poems[page * per_page : (page + 1) * per_page]

    header = t("msg_fav_title", lang, count=len(poems))
    await message.answer(header, parse_mode="Markdown")

    for poem in page_poems:
        card = format_poem_card(poem, max_len=300)
        poem_id = str(poem["id"])
        await message.answer(
            card,
            reply_markup=poem_action_keyboard(poem_id, is_new=False, lang=lang, is_favorite=True),
            parse_mode="Markdown",
        )

    if total_pages > 1:
        await message.answer(
            f"{page + 1}/{total_pages}",
            reply_markup=favorites_pagination_keyboard(page, total_pages, lang),
        )


async def _send_history(message: Message, telegram_id: int, status_filter: str | None = None) -> None:
    """Show user's learning history with status filter."""
    lang = await get_user_lang(telegram_id)
    try:
        items = await api.get_history(telegram_id, limit=50, status=status_filter)
    except Exception as e:
        logger.error(f"Failed to load history: {e}")
        await message.answer(t("msg_error_generic", lang))
        return

    active = status_filter or "all"
    if not items:
        await message.answer(
            t("msg_hist_empty", lang),
            reply_markup=history_filter_keyboard(lang, active),
        )
        return

    status_emojis = {"new": "📖", "learning": "📖", "reviewing": "🔄", "memorized": "🌟"}

    header = t("msg_hist_title", lang, count=len(items))
    lines = [header, ""]
    for i, item in enumerate(items[:20], 1):
        poem = item.get("poem") or {}
        title = escape_md(poem.get("title", "???"))
        author = escape_md(poem.get("author", "???"))
        status = item.get("status", "new")
        emoji = status_emojis.get(status, "📖")
        last = item.get("last_reviewed_at")
        date_str = last[:10] if last else "—"
        lines.append(f"{i}. {emoji} **{title}** — _{author}_ · {date_str}")

    await message.answer(
        "\n".join(lines),
        reply_markup=history_filter_keyboard(lang, active),
        parse_mode="Markdown",
    )


async def _send_collection_page(message: Message, telegram_id: int, slug: str, page: int) -> None:
    """Show poems from a collection with pagination."""
    lang = await get_user_lang(telegram_id)
    try:
        col = await api.get_collection(slug)
    except Exception as e:
        logger.error(f"Failed to load collection {slug}: {e}")
        await message.answer(t("msg_error_generic", lang))
        return

    title_key = "title_ru" if lang == "ru" else "title_en"
    title = col.get(title_key, slug)
    emoji = col.get("cover_emoji", "📚")
    poems = col.get("poems", [])

    if not poems:
        await message.answer(t("msg_not_found", lang))
        return

    per_page = 5
    total_pages = max(1, (len(poems) + per_page - 1) // per_page)
    page = min(page, total_pages - 1)
    page_poems = poems[page * per_page : (page + 1) * per_page]

    header = t("msg_collection_intro", lang, emoji=emoji, title=escape_md(title), count=len(poems))
    await message.answer(header, parse_mode="Markdown")

    for poem in page_poems:
        card = format_poem_card(poem, max_len=300)
        poem_id = str(poem["id"])
        await message.answer(
            card,
            reply_markup=poem_action_keyboard(poem_id, is_new=True, lang=lang),
            parse_mode="Markdown",
        )

    if total_pages > 1:
        await message.answer(
            f"{page + 1}/{total_pages}",
            reply_markup=collection_pagination_keyboard(slug, page, total_pages, lang),
        )


# ─── Stanza Helpers ──────────────────────────────────────────

async def _send_stanza_view(
    message: Message,
    stanzas: list[str],
    idx: int,
    completed: set[int],
    lang: str,
    edit: bool = False,
) -> None:
    """Show the current stanza with progress and action buttons."""
    total = len(stanzas)
    progress_bar = build_stanza_progress(completed, total)
    progress_line = t("msg_stanza_progress", lang, bar=progress_bar, done=len(completed), total=total)

    parts: list[str] = []
    # Show completed stanzas collapsed
    for i in range(idx):
        if i in completed:
            parts.append(f"_✅ {t('msg_stanza_completed', lang, n=i + 1)}_")

    # Current stanza header + text
    header = t("msg_stanza_header", lang, current=idx + 1, total=total)
    parts.append(f"\n{header}\n\n{stanzas[idx]}")
    parts.append(f"\n{progress_line}")

    text = "\n".join(parts)

    if edit:
        try:
            await message.edit_text(text, reply_markup=stanza_viewing_keyboard(lang), parse_mode="Markdown")
            return
        except Exception:
            pass
    await message.answer(text, reply_markup=stanza_viewing_keyboard(lang), parse_mode="Markdown")


async def _handle_stanza_result(
    message: Message, state: FSMContext, accuracy: float, lang: str
) -> None:
    """Process stanza recitation result — advance on success, offer retry on fail."""
    data = await state.get_data()
    stanzas = data.get("stanzas", [])
    idx = data.get("current_stanza_idx", 0)
    completed = set(data.get("completed_stanzas", []))

    if accuracy >= 60:
        completed.add(idx)
        await state.update_data(completed_stanzas=list(completed))
        await message.answer(
            t("msg_stanza_success", lang, accuracy=f"{accuracy:.0f}"),
            parse_mode="Markdown",
        )
        # Check if all stanzas done
        if len(completed) >= len(stanzas):
            await _finish_stanza_mode(message, state, message.from_user.id)
        else:
            # Auto-advance to next uncompleted stanza
            next_idx = _next_uncompleted(idx, stanzas, completed)
            await state.update_data(current_stanza_idx=next_idx)
            await state.set_state(StanzaFlow.viewing_stanza)
            await _send_stanza_view(message, stanzas, next_idx, completed, lang)
    else:
        await state.set_state(StanzaFlow.viewing_stanza)
        await message.answer(
            t("msg_stanza_fail", lang, accuracy=f"{accuracy:.0f}"),
            reply_markup=stanza_result_keyboard(lang),
            parse_mode="Markdown",
        )


async def _advance_stanza(callback: CallbackQuery, state: FSMContext) -> None:
    """Move to the next stanza (skip)."""
    data = await state.get_data()
    stanzas = data.get("stanzas", [])
    idx = data.get("current_stanza_idx", 0)
    completed = set(data.get("completed_stanzas", []))
    lang = await get_user_lang(callback.from_user.id)

    next_idx = (idx + 1) % len(stanzas)
    # If all visited, wrap around; if all completed, finish
    if len(completed) >= len(stanzas):
        await _finish_stanza_mode(callback.message, state, callback.from_user.id)
        return

    await state.update_data(current_stanza_idx=next_idx)
    await _send_stanza_view(callback.message, stanzas, next_idx, completed, lang, edit=True)


async def _peek_stanza(callback: CallbackQuery, state: FSMContext) -> None:
    """Show the stanza text for reference."""
    data = await state.get_data()
    stanzas = data.get("stanzas", [])
    idx = data.get("current_stanza_idx", 0)
    lang = await get_user_lang(callback.from_user.id)

    stanza_text = stanzas[idx] if idx < len(stanzas) else ""
    await callback.message.answer(
        t("msg_stanza_peek", lang, text=stanza_text),
        reply_markup=stanza_viewing_keyboard(lang),
        parse_mode="Markdown",
    )


async def _finish_stanza_mode(
    message: Message, state: FSMContext, telegram_id: int
) -> None:
    """Complete stanza mode — update SM-2 and award bonus XP."""
    data = await state.get_data()
    poem_id = data.get("poem_id", "")
    lang = await get_user_lang(telegram_id)

    try:
        # Update SM-2 with quality=4 for completing stanza mode
        user_before = await api.get_user(telegram_id)
        level_before = user_before.get("level", 1)

        await api.review_poem(telegram_id, poem_id, 4)

        user_after = await api.get_user(telegram_id)
        level_after = user_after.get("level", 1)

        level_up = level_after if level_after > level_before else None

        from app.utils import format_celebration
        celebration = format_celebration(
            xp=50,
            level_up=level_up,
            challenge_progress=None,
            new_badges=[],
            freeze_used=False,
            freezes_left=user_after.get("streak_freezes_available", 0),
            lang=lang,
        )

        await message.answer(
            t("msg_stanza_all_done", lang) + "\n" + celebration + "\n\n" + t("msg_whats_next", lang),
            reply_markup=post_stanza_keyboard(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Stanza finish failed: {e}")
        await message.answer(
            t("msg_stanza_all_done", lang),
            reply_markup=post_stanza_keyboard(lang),
            parse_mode="Markdown",
        )

    await state.clear()


def _next_uncompleted(current: int, stanzas: list[str], completed: set[int]) -> int:
    """Find the next uncompleted stanza index after current."""
    total = len(stanzas)
    for offset in range(1, total + 1):
        idx = (current + offset) % total
        if idx not in completed:
            return idx
    return (current + 1) % total

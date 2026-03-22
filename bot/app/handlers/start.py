"""Bot command and callback handlers."""

import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.services.api_client import api
from app.translations import t
from app.keyboards.menus import (
    ui_language_keyboard,
    poem_language_keyboard,
    main_menu_keyboard,
    new_poem_method_keyboard,
    poem_action_keyboard,
    review_score_keyboard,
    settings_keyboard,
    cancel_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()

class RecommendFlow(StatesGroup):
    waiting_for_mood = State()
    waiting_for_url = State()

async def get_user_lang(telegram_id: int) -> str:
    """Helper to get user's ui_language, defaults to ru."""
    try:
        user = await api.get_user(telegram_id)
        return user.get("ui_language", "ru")
    except Exception:
        return "ru"

# ─── Global Cancel state ────────────────────────────────────
@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    await state.clear()
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(t("btn_cancel", lang))
    await callback.answer()


# ─── Commands ───────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start — register user and show UI language selection."""
    user = message.from_user
    if not user:
        return

    try:
        await api.create_user(user.id, user.username, user.first_name)
    except Exception as e:
        logger.error(f"Failed to create user: {e}")

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

    try:
        users = await api.get_leaderboard()
    except Exception as e:
        logger.error(f"Failed to fetch leaderboard: {e}")
        await message.answer("❌ Failed to load leaderboard.")
        return

    if not users:
        await message.answer("🏆 The leaderboard is currently empty.")
        return

    text = "🏆 **Global Leaderboard** 🏆\n\n"
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
        
        text += f"{emoji} **{name}** - Lvl {level} ({xp} XP) 🔥{streak}\n"

    await message.answer(text, parse_mode="Markdown")


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

    await callback.message.delete()
    await callback.message.answer(
        t("btn_poem_lang", lang) + ":",
        reply_markup=poem_language_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()

@router.callback_query(F.data.startswith("settings_"))
async def cb_settings_actions(callback: CallbackQuery) -> None:
    if not callback.data or not callback.from_user:
        return
    action = callback.data.replace("settings_", "")
    lang = await get_user_lang(callback.from_user.id)
    
    if action == "ui_lang":
        await callback.message.edit_text("🇺🇳 UI Language", reply_markup=ui_language_keyboard())
    elif action == "poem_lang":
        await callback.message.edit_text("📚 Poetry Language", reply_markup=poem_language_keyboard())
    elif action == "notif_time":
        await callback.message.answer("Feature in development!") # Placeholder for time selection
    await callback.answer()

@router.callback_query(F.data.startswith("lang_"))
async def cb_poetry_language(callback: CallbackQuery) -> None:
    """Handle Poetry language selection."""
    if not callback.data or not callback.from_user:
        return
    lang_pref = callback.data.replace("lang_", "")

    try:
        await api.update_user(callback.from_user.id, language_pref=lang_pref)
    except Exception as e:
        logger.error(f"Failed to update language: {e}")

    lang = await get_user_lang(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(
        "✅ Saved!",
        reply_markup=main_menu_keyboard(lang),
        parse_mode="Markdown",
    )
    await callback.answer()


# ─── New Poem Flow Callbacks ──────────────────────────────

@router.callback_query(F.data == "new_surprise")
async def cb_new_surprise(callback: CallbackQuery) -> None:
    if not callback.from_user or not callback.message:
        return
    await callback.message.delete()
    await _send_recommendation(callback.message, callback.from_user.id, mood=None)
    await callback.answer()

@router.callback_query(F.data == "new_mood")
async def cb_new_mood(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        t("msg_ask_mood", lang),
        reply_markup=cancel_keyboard(lang)
    )
    await state.set_state(RecommendFlow.waiting_for_mood)
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
    if not message.from_user or not message.text:
        return
    await state.clear()
    lang = await get_user_lang(message.from_user.id)
    wait_msg = await message.answer(t("msg_analyzing", lang))
    await _send_recommendation(message, message.from_user.id, mood=message.text)
    
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
            f"📖 **{poem['title']}**\n*{poem['author']}*\n\n{poem['text'][:3500]}",
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
    if not callback.data or not callback.message:
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
        
        bonus_msg = ""
        if level_after > level_before:
            bonus_msg = "\n" + t("msg_level_up", lang, level=level_after)
        else:
            bonus_msg = "\n" + t("msg_xp_gain", lang, xp=15)

        status_emoji = {
            "learning": "📖", "reviewing": "🔄", "memorized": "🌟"
        }.get(result.get("status", ""), "📚")

        await callback.message.edit_text(
            f"{status_emoji} {bonus_msg}",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Review failed: {e}")
        await callback.message.answer("❌ Error")

    await callback.answer()

@router.callback_query(F.data == "skip")
async def cb_skip(callback: CallbackQuery, state: FSMContext) -> None:
    if not callback.from_user or not callback.message:
        return
    await callback.message.delete()
    await _send_recommendation(callback.message, callback.from_user.id, mood=None, length=None)
    await callback.answer()


# ─── Free Text Handler ──────────────────────────────────────
@router.message(F.text)
async def handle_text(message: Message) -> None:
    """Handle unknown text."""
    if not message.from_user:
        return
    lang = await get_user_lang(message.from_user.id)
    await message.answer(
        "👋",
        reply_markup=main_menu_keyboard(lang),
    )


# ─── Helpers ────────────────────────────────────────────────

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
        
        title = poem_full["title"]
        author = poem_full["author"]
        text = poem_full["text"]

        if len(text) > 3500:
            text = text[:3500] + "\n..."

        await message.answer(
            f"📖 **{title}**\n*{author}*\n\n{text}",
            reply_markup=poem_action_keyboard(poem_id, is_new=True, lang=lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        await message.answer(t("msg_not_found", lang))


async def _send_review(message: Message, telegram_id: int) -> None:
    """Show poems that are due for review."""
    lang = await get_user_lang(telegram_id)
    try:
        due = await api.get_due_reviews(telegram_id)
        if not due:
            await message.answer("✅ Отлично! Нет стихов для повторения.")
            return

        for mem in due[:3]:
            poem = await api.get_poem(mem["poem_id"])
            await message.answer(
                f"🔄 **{poem['title']}**\n*{poem['author']}*\n\n"
                f"{poem['text'][:500]}...",
                reply_markup=poem_action_keyboard(poem["id"], is_new=False, lang=lang),
                parse_mode="Markdown",
            )
    except Exception as e:
        logger.error(f"Review fetch failed: {e}")
        await message.answer("❌ Error")


async def _send_progress(message: Message, telegram_id: int) -> None:
    """Show user's profile card."""
    lang = await get_user_lang(telegram_id)
    try:
        user = await api.get_user(telegram_id)
        stats = await api.get_progress(telegram_id)
        
        next_obj = user.get("level", 1) * 100
        
        profile_text = t(
            "msg_profile", 
            lang,
            level=user.get("level", 1),
            xp=user.get("xp", 0),
            next_level_xp=next_obj,
            streak=user.get("streak", 0),
            learning=stats.get('learning', 0),
            reviewing=stats.get('reviewing', 0),
            memorized=stats.get('memorized', 0),
            total=stats.get('total', 0),
            due=stats.get('due_for_review', 0)
        )
        
        await message.answer(
            profile_text,
            reply_markup=main_menu_keyboard(lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Progress fetch failed: {e}")
        await message.answer("❌ Error")

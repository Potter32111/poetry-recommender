"""Bot command and callback handlers."""

import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from app.services.api_client import api
from app.keyboards.menus import (
    language_keyboard,
    poem_action_keyboard,
    review_score_keyboard,
    main_menu_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()


# ─── Commands ───────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start — register user and show language selection."""
    user = message.from_user
    if not user:
        return

    try:
        await api.create_user(user.id, user.username, user.first_name)
    except Exception as e:
        logger.error(f"Failed to create user: {e}")

    await message.answer(
        f"👋 Welcome to **Poetry Companion**, {user.first_name or 'friend'}!\n\n"
        "I'll help you discover and memorize classic poems.\n"
        "Choose your preferred language:",
        reply_markup=language_keyboard(),
        parse_mode="Markdown",
    )


@router.message(Command("recommend"))
async def cmd_recommend(message: Message) -> None:
    """Handle /recommend — get a poem recommendation."""
    if not message.from_user:
        return
    await _send_recommendation(message, message.from_user.id)


@router.message(Command("review"))
async def cmd_review(message: Message) -> None:
    """Handle /review — show poems due for review."""
    if not message.from_user:
        return
    await _send_review(message, message.from_user.id)


@router.message(Command("progress"))
async def cmd_progress(message: Message) -> None:
    """Handle /progress — show memorization stats."""
    if not message.from_user:
        return
    await _send_progress(message, message.from_user.id)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help — show available commands."""
    await message.answer(
        "📚 **Poetry Companion Commands:**\n\n"
        "/recommend — Get a new poem\n"
        "/review — Review poems due today\n"
        "/progress — Your memorization stats\n"
        "/help — Show this message\n\n"
        "You can also send me any message and I'll suggest a poem!",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    """Handle /menu — show main menu."""
    await message.answer("What would you like to do?", reply_markup=main_menu_keyboard())


# ─── Callbacks ──────────────────────────────────────────────

@router.callback_query(F.data.startswith("lang_"))
async def cb_language(callback: CallbackQuery) -> None:
    """Handle language selection."""
    if not callback.data or not callback.from_user:
        return
    lang = callback.data.replace("lang_", "")

    try:
        await api.update_user(callback.from_user.id, language_pref=lang)
    except Exception as e:
        logger.error(f"Failed to update language: {e}")

    lang_names = {"en": "English 🇬🇧", "ru": "Русский 🇷🇺", "both": "Both 🌍"}
    await callback.message.edit_text(
        f"✅ Language set to **{lang_names.get(lang, lang)}**!\n\n"
        "Now let's find you a poem! Use /recommend or tap below:",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "recommend")
async def cb_recommend(callback: CallbackQuery) -> None:
    """Handle recommend button."""
    if not callback.from_user or not callback.message:
        return
    await _send_recommendation(callback.message, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "review")
async def cb_review(callback: CallbackQuery) -> None:
    """Handle review button."""
    if not callback.from_user or not callback.message:
        return
    await _send_review(callback.message, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "progress")
async def cb_progress(callback: CallbackQuery) -> None:
    """Handle progress button."""
    if not callback.from_user or not callback.message:
        return
    await _send_progress(callback.message, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("learn_"))
async def cb_learn(callback: CallbackQuery) -> None:
    """Handle 'Learn this' — show review score options."""
    if not callback.data or not callback.message:
        return
    poem_id = callback.data.replace("learn_", "")
    await callback.message.answer(
        "📝 Try to recite the poem from memory, then rate your recall:",
        reply_markup=review_score_keyboard(poem_id),
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

    try:
        result = await api.review_poem(callback.from_user.id, poem_id, score)
        status = result.get("status", "unknown")
        interval = result.get("interval_days", 0)

        status_emoji = {
            "learning": "📖", "reviewing": "🔄", "memorized": "🌟"
        }.get(status, "📚")

        await callback.message.edit_text(
            f"{status_emoji} **Review recorded!**\n\n"
            f"Status: {status}\n"
            f"Next review in: {interval} day(s)\n\n"
            "Keep it up! 💪",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Review failed: {e}")
        await callback.message.answer("❌ Could not record review. Please try again.")

    await callback.answer()


@router.callback_query(F.data == "skip")
async def cb_skip(callback: CallbackQuery) -> None:
    """Handle skip — get another recommendation."""
    if not callback.from_user or not callback.message:
        return
    await _send_recommendation(callback.message, callback.from_user.id)
    await callback.answer()


@router.message(F.text)
async def handle_text(message: Message) -> None:
    """Handle free text — show menu."""
    if not message.from_user:
        return
    await message.answer(
        "📚 What would you like to do?",
        reply_markup=main_menu_keyboard(),
    )


# ─── Helpers ────────────────────────────────────────────────

async def _send_recommendation(message: Message, telegram_id: int) -> None:
    """Fetch and send a smart poem recommendation."""
    try:
        # Fetch 1 recommendation using our new pgvector-based recommender
        recs = await api.get_pgvector_recommendations(telegram_id, limit=1)
        if not recs:
            raise ValueError("No recommendations returned")
            
        rec_poem = recs[0]
        poem_id = rec_poem["id"]
        
        # Fetch the full text for the recommended poem
        poem_full = await api.get_poem(poem_id)
        
        title = poem_full["title"]
        author = poem_full["author"]
        text = poem_full["text"]

        # Truncate if too long for Telegram
        if len(text) > 3500:
            text = text[:3500] + "\n..."

        await message.answer(
            f"📖 **{title}**\n*{author}*\n\n{text}",
            reply_markup=poem_action_keyboard(poem_id),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        await message.answer(
            "😔 No poems available right now. Try again later!",
            reply_markup=main_menu_keyboard(),
        )


async def _send_review(message: Message, telegram_id: int) -> None:
    """Show poems that are due for review."""
    try:
        due = await api.get_due_reviews(telegram_id)
        if not due:
            await message.answer(
                "✅ No poems due for review! Great job!\n\nWant a new poem?",
                reply_markup=main_menu_keyboard(),
            )
            return

        for mem in due[:3]:
            poem = await api.get_poem(mem["poem_id"])
            await message.answer(
                f"🔄 **Review: {poem['title']}**\n*{poem['author']}*\n\n"
                f"{poem['text'][:1000]}\n\n"
                "Rate your recall:",
                reply_markup=review_score_keyboard(poem["id"]),
                parse_mode="Markdown",
            )
    except Exception as e:
        logger.error(f"Review fetch failed: {e}")
        await message.answer("❌ Could not load reviews. Try again later.")


async def _send_progress(message: Message, telegram_id: int) -> None:
    """Show user's memorization progress."""
    try:
        stats = await api.get_progress(telegram_id)
        await message.answer(
            "📊 **Your Progress:**\n\n"
            f"📖 New: {stats.get('new', 0)}\n"
            f"📚 Learning: {stats.get('learning', 0)}\n"
            f"🔄 Reviewing: {stats.get('reviewing', 0)}\n"
            f"🌟 Memorized: {stats.get('memorized', 0)}\n"
            f"📋 Total: {stats.get('total', 0)}\n"
            f"⏰ Due for review: {stats.get('due_for_review', 0)}",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Progress fetch failed: {e}")
        await message.answer("❌ Could not load progress. Are you registered? Try /start")

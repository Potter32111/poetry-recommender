"""Voice message handler for poem recitation checking."""

import io
import logging

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.services.api_client import api
from app.translations import t
from app.utils import get_user_lang, format_poem_card, escape_md, format_celebration
from app.keyboards.menus import poem_action_keyboard, recite_prompt_keyboard

logger = logging.getLogger(__name__)
router = Router()


class ReciteStates(StatesGroup):
    """FSM states for voice recitation flow."""
    waiting_voice = State()
    waiting_text = State()


# ─── Callback: Start recitation ─────────────────────────────

@router.callback_query(F.data.startswith("recite_"))
async def cb_recite(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle 'Recite' button — ask user to send voice message."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    poem_id = callback.data.replace("recite_", "")
    lang = await get_user_lang(callback.from_user.id)
    await state.set_state(ReciteStates.waiting_voice)
    await state.update_data(poem_id=poem_id, hints_used=0, hint_line_idx=0)
    await callback.message.answer(
        t("msg_recite_prompt", lang),
        parse_mode="Markdown",
        reply_markup=recite_prompt_keyboard(poem_id, lang),
    )
    await callback.answer()


# ─── Handler: Receive voice message ─────────────────────────

@router.message(ReciteStates.waiting_voice, F.voice)
async def handle_voice(message: Message, state: FSMContext, bot: Bot) -> None:
    """Process voice message — download, send to backend, show result."""
    if not message.from_user or not message.voice:
        return

    lang = await get_user_lang(message.from_user.id)
    data = await state.get_data()
    poem_id = data.get("poem_id")
    if not poem_id:
        await message.answer(t("msg_no_poem_selected", lang))
        await state.clear()
        return

    # Show processing indicator
    processing_msg = await message.answer(t("msg_processing", lang))

    try:
        # Download voice file
        voice_file = await bot.get_file(message.voice.file_id)
        voice_bytes = io.BytesIO()
        await bot.download_file(voice_file.file_path, voice_bytes)
        audio_data = voice_bytes.getvalue()

        # Check gamification status before and after
        user_before = await api.get_user(message.from_user.id)
        level_before = user_before.get("level", 1)

        result = await api.check_voice(message.from_user.id, poem_id, audio_data)
        
        user_after = await api.get_user(message.from_user.id)
        level_after = user_after.get("level", 1)
        lang = user_after.get("ui_language", "ru")
        
        level_up = level_after if level_after > level_before else None

        # Build celebration cascade
        new_badges = result.get("new_badges", [])
        challenge_info = result.get("challenge_progress")
        freeze_used = result.get("streak_freeze_used", False)
        celebration = format_celebration(
            xp=30,
            level_up=level_up,
            challenge_progress=challenge_info,
            new_badges=new_badges,
            freeze_used=freeze_used,
            freezes_left=user_after.get("streak_freezes_available", 0),
            lang=lang,
        )

        # Hints penalty info
        hints_used = data.get("hints_used", 0)
        hints_msg = ""
        if hints_used > 0:
            penalty = hints_used * 5
            hints_msg = "\n" + t("msg_hints_penalty", lang, count=hints_used, xp=penalty)

        # Format result
        response_text = _format_voice_result(result, lang) + "\n" + celebration + hints_msg

        # Delete processing message and send result
        try:
            await processing_msg.delete()
        except Exception:
            pass

        await message.answer(
            response_text,
            reply_markup=poem_action_keyboard(poem_id, is_new=False, lang=lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Voice check failed: {e}")
        try:
            await processing_msg.delete()
        except Exception:
            pass
        await message.answer(
            t("msg_voice_error", lang),
            reply_markup=poem_action_keyboard(poem_id, is_new=False, lang=lang),
        )

    await state.clear()


# ─── Handler: Non-voice message while waiting ───────────────

@router.message(ReciteStates.waiting_voice)
async def handle_not_voice(message: Message, state: FSMContext) -> None:
    """Handle text/other messages when expecting voice."""
    lang = await get_user_lang(message.from_user.id) if message.from_user else "ru"
    await message.answer(
        t("msg_voice_not_text", lang),
        parse_mode="Markdown",
    )


# ─── Callback: Start text recitation ────────────────────────

@router.callback_query(F.data.startswith("type_"))
async def cb_type_recite(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle 'Type it' button — ask user to type the poem from memory."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    poem_id = callback.data.replace("type_", "")
    lang = await get_user_lang(callback.from_user.id)
    await state.set_state(ReciteStates.waiting_text)
    await state.update_data(poem_id=poem_id, hints_used=0, hint_line_idx=0)
    await callback.message.answer(
        t("msg_type_prompt", lang),
        parse_mode="Markdown",
        reply_markup=recite_prompt_keyboard(poem_id, lang),
    )
    await callback.answer()


# ─── Handler: Receive typed text ─────────────────────────────

@router.message(ReciteStates.waiting_text, F.text)
async def handle_text_recite(message: Message, state: FSMContext) -> None:
    """Process typed text — send to backend for comparison, show result."""
    if not message.from_user or not message.text:
        return

    lang = await get_user_lang(message.from_user.id)
    data = await state.get_data()
    poem_id = data.get("poem_id")
    if not poem_id:
        await message.answer(t("msg_no_poem_selected", lang))
        await state.clear()
        return

    processing_msg = await message.answer(t("msg_processing", lang))

    try:
        hints_used = data.get("hints_used", 0)

        user_before = await api.get_user(message.from_user.id)
        level_before = user_before.get("level", 1)

        result = await api.check_text(
            message.from_user.id, poem_id, message.text, hints_used=hints_used
        )

        user_after = await api.get_user(message.from_user.id)
        level_after = user_after.get("level", 1)
        lang = user_after.get("ui_language", "ru")

        level_up = level_after if level_after > level_before else None
        xp = max(0, 20 - hints_used * 5)

        new_badges = result.get("new_badges", [])
        challenge_info = result.get("challenge_progress")
        freeze_used = result.get("streak_freeze_used", False)
        celebration = format_celebration(
            xp=xp,
            level_up=level_up,
            challenge_progress=challenge_info,
            new_badges=new_badges,
            freeze_used=freeze_used,
            freezes_left=user_after.get("streak_freezes_available", 0),
            lang=lang,
        )

        hints_msg = ""
        if hints_used > 0:
            penalty = hints_used * 5
            hints_msg = "\n" + t("msg_hints_penalty", lang, count=hints_used, xp=penalty)

        response_text = _format_voice_result(result, lang) + "\n" + celebration + hints_msg

        try:
            await processing_msg.delete()
        except Exception:
            pass

        await message.answer(
            response_text,
            reply_markup=poem_action_keyboard(poem_id, is_new=False, lang=lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Text check failed: {e}")
        try:
            await processing_msg.delete()
        except Exception:
            pass
        await message.answer(
            t("msg_voice_error", lang),
            reply_markup=poem_action_keyboard(poem_id, is_new=False, lang=lang),
        )

    await state.clear()


# ─── Handler: Voice message while waiting for text ───────────

@router.message(ReciteStates.waiting_text)
async def handle_not_text(message: Message, state: FSMContext) -> None:
    """Handle voice/other messages when expecting text."""
    lang = await get_user_lang(message.from_user.id) if message.from_user else "ru"
    await message.answer(t("msg_type_not_voice", lang))


# ─── Callback: Hint during recitation ───────────────────────

@router.callback_query(F.data.startswith("hint_"))
async def cb_hint(callback: CallbackQuery, state: FSMContext) -> None:
    """Show a hint (first few words of the next unshown poem line)."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    lang = await get_user_lang(callback.from_user.id)
    data = await state.get_data()
    poem_id = data.get("poem_id")
    if not poem_id:
        await callback.answer()
        return

    try:
        poem = await api.get_poem(poem_id)
        lines = [line.strip() for line in poem.get("text", "").split("\n") if line.strip()]

        hint_line_idx = data.get("hint_line_idx", 0)
        if hint_line_idx >= len(lines):
            await callback.message.answer(t("msg_no_more_hints", lang))
            await callback.answer()
            return

        # Show first 3-4 words of the next line
        line = lines[hint_line_idx]
        words = line.split()
        hint_words = " ".join(words[:4])
        await callback.message.answer(
            t("msg_hint_line", lang, words=hint_words),
            parse_mode="Markdown",
        )

        hints_used = data.get("hints_used", 0) + 1
        await state.update_data(hints_used=hints_used, hint_line_idx=hint_line_idx + 1)
    except Exception as e:
        logger.error(f"Hint failed: {e}")
        await callback.message.answer(t("msg_voice_load_error", lang))

    await callback.answer()


# ─── Callback: Try again ────────────────────────────────────

@router.callback_query(F.data.startswith("retry_recite_"))
async def cb_retry_recite(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle 'Try again' — re-enter voice recording state."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    poem_id = callback.data.replace("retry_recite_", "")
    lang = await get_user_lang(callback.from_user.id)
    await state.set_state(ReciteStates.waiting_voice)
    await state.update_data(poem_id=poem_id)

    await callback.message.answer(
        t("msg_voice_retry", lang),
        parse_mode="Markdown",
    )
    await callback.answer()


# ─── Callback: Show poem text ───────────────────────────────

@router.callback_query(F.data.startswith("show_poem_"))
async def cb_show_poem(callback: CallbackQuery) -> None:
    """Handle 'Read poem' — show full poem text."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    poem_id = callback.data.replace("show_poem_", "")
    lang = await get_user_lang(callback.from_user.id)
    try:
        poem = await api.get_poem(poem_id)
        await callback.message.answer(
            format_poem_card(poem),
            reply_markup=poem_action_keyboard(poem_id, lang=lang),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Failed to load poem: {e}")
        await callback.message.answer(t("msg_voice_load_error", lang))
    await callback.answer()


# ─── Callback: TTS — Listen to poem ─────────────────────────

@router.callback_query(F.data.startswith("tts_"))
async def cb_tts(callback: CallbackQuery) -> None:
    """Generate TTS audio and send it as a voice message."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    poem_id = callback.data.replace("tts_", "")
    lang = await get_user_lang(callback.from_user.id)

    processing_msg = await callback.message.answer(t("msg_tts_generating", lang))

    try:
        audio_bytes = await api.get_poem_tts(poem_id)

        try:
            await processing_msg.delete()
        except Exception:
            pass

        voice_file = BufferedInputFile(audio_bytes, filename="poem.mp3")
        await callback.message.answer_voice(voice_file)
    except Exception as e:
        error_str = str(e)
        logger.error(f"TTS failed: {e}")
        try:
            await processing_msg.delete()
        except Exception:
            pass
        if "too long" in error_str or "400" in error_str:
            await callback.message.answer(t("msg_tts_too_long", lang))
        else:
            await callback.message.answer(t("msg_tts_error", lang))

    await callback.answer()


# ─── Helpers ─────────────────────────────────────────────────

def _format_voice_result(result: dict, lang: str) -> str:
    """Format voice check result into a pretty Telegram message."""
    accuracy = result.get("accuracy_percent", 0)
    feedback = result.get("feedback", "")
    missed = result.get("missed_lines", [])
    next_steps = result.get("next_steps", "")
    status = result.get("status", "")
    interval = result.get("interval_days", 0)
    word_details = result.get("word_details", [])

    # Build accuracy bar
    filled = round(accuracy / 10)
    bar = "█" * filled + "░" * (10 - filled)

    text = t("msg_voice_result", lang) + "\n\n"
    text += f"`{bar}` **{accuracy:.0f}%**\n\n"

    # Word-level summary
    if word_details:
        correct_count = sum(1 for w in word_details if w.get("status") in ("correct", "close"))
        total_count = len(word_details)
        text += t("msg_voice_word_summary", lang, correct=correct_count, total=total_count) + "\n"

        # Show up to 2 "close" word examples
        close_words = [w for w in word_details if w.get("status") == "close" and w.get("similar_to")]
        for cw in close_words[:2]:
            said = escape_md(cw["similar_to"])
            expected = escape_md(cw["word"])
            text += t("msg_voice_close_word", lang, said=said, expected=expected) + "\n"
        text += "\n"

    if missed:
        text += t("msg_voice_missed", lang) + "\n"
        for line in missed[:3]:
            text += f"  • _{escape_md(line)}_\n"
        if len(missed) > 3:
            text += "  " + t("msg_voice_more_missed", lang, count=len(missed) - 3) + "\n"
        text += "\n"

    text += f"💬 {feedback}\n\n"

    # Status info
    status_emoji = {
        "learning": "📖", "reviewing": "🔄", "memorized": "🌟"
    }.get(status, "📚")

    next_tip = {
        "repeat": t("msg_voice_next_repeat", lang),
        "read_again": t("msg_voice_next_read", lang),
        "memorized": t("msg_voice_next_memorized", lang),
    }.get(next_steps, "")

    text += t("msg_voice_status", lang, emoji=status_emoji, status=status) + "\n"
    text += t("msg_voice_next_interval", lang, days=interval) + "\n"
    if next_tip:
        text += "\n" + t("msg_voice_tip", lang, tip=next_tip)

    return text

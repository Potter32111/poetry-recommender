"""Voice message handler for poem recitation checking."""

import io
import logging

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.services.api_client import api
from app.translations import t
from app.keyboards.menus import poem_action_keyboard

logger = logging.getLogger(__name__)
router = Router()


class ReciteStates(StatesGroup):
    """FSM states for voice recitation flow."""
    waiting_voice = State()


# ─── Callback: Start recitation ─────────────────────────────

@router.callback_query(F.data.startswith("recite_"))
async def cb_recite(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle 'Recite' button — ask user to send voice message."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    poem_id = callback.data.replace("recite_", "")
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.answer(
        t("msg_recite_prompt", lang),
        parse_mode="Markdown",
    )
    await callback.answer()

async def get_user_lang(telegram_id: int) -> str:
    from app.services.api_client import api
    try:
        user = await api.get_user(telegram_id)
        return user.get("ui_language", "ru")
    except Exception:
        return "ru"


# ─── Handler: Receive voice message ─────────────────────────

@router.message(ReciteStates.waiting_voice, F.voice)
async def handle_voice(message: Message, state: FSMContext, bot: Bot) -> None:
    """Process voice message — download, send to backend, show result."""
    if not message.from_user or not message.voice:
        return

    data = await state.get_data()
    poem_id = data.get("poem_id")
    if not poem_id:
        await message.answer("❌ Ошибка: стих не выбран. Попробуйте /review или /recommend.")
        await state.clear()
        return

    # Show processing indicator
    processing_msg = await message.answer("⏳ Анализирую ваше чтение...")

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
        
        from app.translations import t
        bonus_msg = ""
        if level_after > level_before:
            bonus_msg = "\n" + t("msg_level_up", lang, level=level_after)
        else:
            bonus_msg = "\n" + t("msg_xp_gain", lang, xp=30)

        # Format result
        response_text = _format_voice_result(result) + "\n" + bonus_msg

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
            "❌ Не удалось обработать голосовое сообщение. Попробуйте ещё раз.",
            reply_markup=poem_action_keyboard(poem_id, is_new=False, lang="ru"),
        )

    await state.clear()


# ─── Handler: Non-voice message while waiting ───────────────

@router.message(ReciteStates.waiting_voice)
async def handle_not_voice(message: Message, state: FSMContext) -> None:
    """Handle text/other messages when expecting voice."""
    await message.answer(
        "🎤 Отправьте **голосовое сообщение**, а не текст.\n"
        "Нажмите и удерживайте кнопку микрофона 🎙️",
        parse_mode="Markdown",
    )


# ─── Callback: Try again ────────────────────────────────────

@router.callback_query(F.data.startswith("retry_recite_"))
async def cb_retry_recite(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle 'Try again' — re-enter voice recording state."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    poem_id = callback.data.replace("retry_recite_", "")
    await state.set_state(ReciteStates.waiting_voice)
    await state.update_data(poem_id=poem_id)

    await callback.message.answer(
        "🎤 Попробуйте ещё раз! Запишите голосовое сообщение:",
        parse_mode="Markdown",
    )
    await callback.answer()


# ─── Callback: Show poem text ───────────────────────────────

@router.callback_query(F.data.startswith("show_poem_"))
async def cb_show_poem(callback: CallbackQuery) -> None:
    """Handle 'Read poem' — show full poem text."""
    if not callback.data or not callback.message:
        return

    poem_id = callback.data.replace("show_poem_", "")
    try:
        poem = await api.get_poem(poem_id)
        text = poem["text"]
        if len(text) > 3500:
            text = text[:3500] + "\n..."

        await callback.message.answer(
            f"📖 **{poem['title']}**\n*{poem['author']}*\n\n{text}",
            reply_markup=poem_action_keyboard(poem_id),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Failed to load poem: {e}")
        await callback.message.answer("❌ Не удалось загрузить стих.")
    await callback.answer()


# ─── Helpers ─────────────────────────────────────────────────

def _format_voice_result(result: dict) -> str:
    """Format voice check result into a pretty Telegram message."""
    accuracy = result.get("accuracy_percent", 0)
    feedback = result.get("feedback", "")
    missed = result.get("missed_lines", [])
    next_steps = result.get("next_steps", "")
    status = result.get("status", "")
    interval = result.get("interval_days", 0)

    # Build accuracy bar
    filled = round(accuracy / 10)
    bar = "█" * filled + "░" * (10 - filled)

    text = f"🎤 **Результат проверки:**\n\n"
    text += f"`{bar}` **{accuracy:.0f}%**\n\n"

    if missed:
        text += "❌ **Пропущено:**\n"
        for line in missed[:5]:  # Show max 5 missed lines
            text += f"  • _{line}_\n"
        if len(missed) > 5:
            text += f"  _...и ещё {len(missed) - 5} строк(и)_\n"
        text += "\n"

    text += f"💬 {feedback}\n\n"

    # Status info
    status_emoji = {
        "learning": "📖", "reviewing": "🔄", "memorized": "🌟"
    }.get(status, "📚")

    next_emoji = {
        "repeat": "🔄 Попробуйте ещё раз",
        "read_again": "📖 Перечитайте стих",
        "memorized": "🌟 Стих выучен!",
    }.get(next_steps, "")

    text += f"{status_emoji} Статус: {status}\n"
    text += f"📅 Следующий повтор через: {interval} дн.\n"
    if next_emoji:
        text += f"\n📋 **Рекомендация:** {next_emoji}"

    return text

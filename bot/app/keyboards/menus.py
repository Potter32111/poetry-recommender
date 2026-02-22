"""Inline keyboards for the bot."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        ],
        [InlineKeyboardButton(text="🌍 Both / Оба", callback_data="lang_both")],
    ])


def poem_action_keyboard(poem_id: str) -> InlineKeyboardMarkup:
    """Action buttons after a poem is shown."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎤 Recite", callback_data=f"recite_{poem_id}"),
            InlineKeyboardButton(text="📝 Learn this", callback_data=f"learn_{poem_id}"),
        ],
        [
            InlineKeyboardButton(text="⏭️ Skip", callback_data="skip"),
            InlineKeyboardButton(text="📊 My Progress", callback_data="progress"),
        ],
    ])


def review_score_keyboard(poem_id: str) -> InlineKeyboardMarkup:
    """Score buttons for SM-2 review (0-5)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="0 😵 Blank", callback_data=f"score_{poem_id}_0"),
            InlineKeyboardButton(text="1 😰 Wrong", callback_data=f"score_{poem_id}_1"),
            InlineKeyboardButton(text="2 😕 Hard", callback_data=f"score_{poem_id}_2"),
        ],
        [
            InlineKeyboardButton(text="3 🤔 OK", callback_data=f"score_{poem_id}_3"),
            InlineKeyboardButton(text="4 😊 Good", callback_data=f"score_{poem_id}_4"),
            InlineKeyboardButton(text="5 🌟 Perfect", callback_data=f"score_{poem_id}_5"),
        ],
        [InlineKeyboardButton(text="🎤 Recite instead", callback_data=f"recite_{poem_id}")],
    ])


def voice_feedback_keyboard(poem_id: str) -> InlineKeyboardMarkup:
    """Buttons shown after voice evaluation."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Try again", callback_data=f"retry_recite_{poem_id}"),
            InlineKeyboardButton(text="📖 Read poem", callback_data=f"show_poem_{poem_id}"),
        ],
        [
            InlineKeyboardButton(text="➡️ Next poem", callback_data="recommend"),
            InlineKeyboardButton(text="📊 Progress", callback_data="progress"),
        ],
    ])


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Get a Poem", callback_data="recommend")],
        [InlineKeyboardButton(text="🔄 Review Due", callback_data="review")],
        [InlineKeyboardButton(text="📊 My Progress", callback_data="progress")],
    ])

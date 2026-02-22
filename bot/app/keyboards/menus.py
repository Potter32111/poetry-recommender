"""Keyboards for the bot."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from app.translations import t


def ui_language_keyboard() -> InlineKeyboardMarkup:
    """UI Language selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ui_lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="ui_lang_en"),
        ]
    ])


def poem_language_keyboard() -> InlineKeyboardMarkup:
    """Poetry language selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ],
        [InlineKeyboardButton(text="🌍 Both / Оба", callback_data="lang_both")],
    ])


def main_menu_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Persistent bottom menu."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_new", lang)), KeyboardButton(text=t("btn_review", lang))],
            [KeyboardButton(text=t("btn_profile", lang)), KeyboardButton(text=t("btn_settings", lang))]
        ],
        resize_keyboard=True,
        persistent=True
    )


def new_poem_method_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Options for getting a new poem."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_surprise", lang), callback_data="new_surprise")],
        [InlineKeyboardButton(text=t("btn_mood", lang), callback_data="new_mood")],
        [InlineKeyboardButton(text=t("btn_url", lang), callback_data="new_url")],
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel")],
    ])


def cancel_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Generic cancel button for FSM states."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_cancel", lang), callback_data="cancel")]
    ])


def poem_action_keyboard(poem_id: str, is_new: bool = True, lang: str = "ru") -> InlineKeyboardMarkup:
    """Action buttons after a poem is shown."""
    buttons = [
        [
            InlineKeyboardButton(text=t("btn_recite", lang), callback_data=f"recite_{poem_id}"),
            InlineKeyboardButton(text=t("btn_flashcard", lang), callback_data=f"learn_{poem_id}"),
        ]
    ]
    if is_new:
        buttons.append([InlineKeyboardButton(text=t("btn_skip", lang), callback_data="skip")])
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
    ])


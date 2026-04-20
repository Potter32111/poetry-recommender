"""Background scheduler for daily engagement notifications."""
import logging
import random
from datetime import datetime
import asyncio
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.services.api_client import api
from app.translations import t

logger = logging.getLogger(__name__)


def _review_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Inline keyboard with Start Review button."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_start_review", lang), callback_data="menu_review")],
    ])


def _poem_of_day_keyboard(poem_id: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Inline keyboard with Read Poem button."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_read_poem", lang), callback_data=f"learn_{poem_id}")],
    ])


async def process_daily_notifications(bot: Bot):
    """Job to send daily review reminders based on user's preferred time."""
    logger.info("Running hourly notification job...")
    try:
        users_with_due = await api.get_all_due_reviews()
        current_hour = datetime.now().hour

        for u in users_with_due:
            user_id = u["telegram_id"]
            user_time = u.get("notification_time", "10:00")

            try:
                preferred_hour = int(user_time.split(":")[0])
            except (ValueError, AttributeError):
                preferred_hour = 10

            if current_hour != preferred_hour:
                continue

            lang = u.get("ui_language", "ru")
            count = u.get("due_count", 1)
            streak = u.get("streak", 0)
            msg = t("push_review", lang, count=count, streak=streak)

            # Append daily challenge info
            try:
                challenge = await api.get_today_challenge(user_id)
                if challenge and not challenge.get("completed_at"):
                    from app.utils import _challenge_goal_text
                    goal = _challenge_goal_text(
                        challenge.get("goal_type", ""),
                        challenge.get("goal_target", 1),
                        lang,
                    )
                    msg += "\n" + t(
                        "msg_challenge_progress", lang,
                        goal=goal,
                        progress=challenge.get("current_progress", 0),
                        target=challenge.get("goal_target", 1),
                    )
            except Exception:
                pass

            try:
                await bot.send_message(
                    user_id, msg, reply_markup=_review_keyboard(lang),
                )
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Failed to send review push to {user_id}: {e}")

    except Exception as e:
        logger.error(f"Failed to run hourly notifications: {e}")


async def process_poem_of_day(bot: Bot):
    """Daily job: send a random poem to users who haven't reviewed today."""
    logger.info("Running poem-of-the-day job...")
    try:
        poem_count_resp = await api.get_poem_count()
        total = poem_count_resp.get("count", 0)
        if total == 0:
            logger.warning("No poems in DB — skipping poem of the day.")
            return

        offset = random.randint(0, max(total - 1, 0))
        poems = await api.list_poems(limit=1, offset=offset)
        if not poems:
            logger.warning("Empty poem list — skipping poem of the day.")
            return

        poem = poems[0]
        poem_id = str(poem["id"])
        author = poem.get("author", "???")
        title = poem.get("title", "???")

        # Get users with due reviews — they are already active, don't spam them
        users_with_due = await api.get_all_due_reviews()
        active_tg_ids = {u["telegram_id"] for u in users_with_due}

        # Get ALL users and find idle ones
        all_users = await api.get_all_users()
        idle_users = [u for u in all_users if u.get("telegram_id") not in active_tg_ids]

        for u in idle_users:
            user_id = u.get("telegram_id")
            if not user_id:
                continue
            lang = u.get("ui_language", "ru")
            msg = t("push_poem_of_day", lang, author=author, title=title)

            try:
                await bot.send_message(
                    user_id, msg, reply_markup=_poem_of_day_keyboard(poem_id, lang),
                )
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Failed to send poem-of-day to {user_id}: {e}")

    except Exception as e:
        logger.error(f"Failed to run poem-of-the-day job: {e}")

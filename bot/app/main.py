"""Poetry Recommender Telegram Bot — Entry Point."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from app.config import bot_settings
from app.handlers.start import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    """Start the bot."""
    if not bot_settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        return

    bot = Bot(token=bot_settings.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Starting Poetry Recommender Bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

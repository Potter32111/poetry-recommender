"""Poetry Recommender Telegram Bot — Entry Point."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import bot_settings
from app.handlers.start import router as start_router
from app.handlers.voice import router as voice_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    """Start the bot."""
    if not bot_settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        return

    bot = Bot(token=bot_settings.telegram_bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers (voice first so FSM handlers take priority)
    dp.include_router(voice_router)
    dp.include_router(start_router)

    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from app.scheduler import process_daily_notifications

    scheduler = AsyncIOScheduler()
    scheduler.add_job(process_daily_notifications, "cron", hour=10, minute=0, args=[bot], id="daily_notifications")
    scheduler.start()

    logger.info("Starting Poetry Recommender Bot with APScheduler...")
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())

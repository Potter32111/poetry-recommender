"""Poetry Recommender Telegram Bot — Entry Point."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault
from app.config import bot_settings
from app.handlers.start import router as start_router
from app.handlers.voice import router as voice_router
from app.services.api_client import api

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def _set_bot_commands(bot: Bot) -> None:
    """Register bot commands for Telegram command suggestions."""
    commands_en = [
        BotCommand(command="start", description="Main menu"),
        BotCommand(command="recommend", description="New poem"),
        BotCommand(command="review", description="Review due poems"),
        BotCommand(command="progress", description="My stats"),
        BotCommand(command="leaderboard", description="Leaderboard"),
        BotCommand(command="settings", description="Settings"),
        BotCommand(command="help", description="Help"),
    ]
    commands_ru = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="recommend", description="Новый стих"),
        BotCommand(command="review", description="Повторение"),
        BotCommand(command="progress", description="Моя статистика"),
        BotCommand(command="leaderboard", description="Лидеры"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands_en, scope=BotCommandScopeDefault(), language_code="en")
    await bot.set_my_commands(commands_ru, scope=BotCommandScopeDefault(), language_code="ru")
    # Default (no language) — bilingual descriptions
    commands_default = [
        BotCommand(command="start", description="Main menu / Главное меню"),
        BotCommand(command="recommend", description="New poem / Новый стих"),
        BotCommand(command="review", description="Review due / Повторение"),
        BotCommand(command="progress", description="My stats / Моя статистика"),
        BotCommand(command="leaderboard", description="Leaderboard / Лидеры"),
        BotCommand(command="settings", description="Settings / Настройки"),
        BotCommand(command="help", description="Help / Помощь"),
    ]
    await bot.set_my_commands(commands_default, scope=BotCommandScopeDefault())


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
    from app.scheduler import process_daily_notifications, process_poem_of_day

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        process_daily_notifications, "cron", minute=0,
        args=[bot], id="hourly_notifications",
    )
    scheduler.add_job(
        process_poem_of_day, "cron", hour=9, minute=0,
        args=[bot], id="poem_of_day",
    )
    scheduler.start()

    await _set_bot_commands(bot)
    logger.info("Starting Poetry Recommender Bot with APScheduler...")
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await api.close()

if __name__ == "__main__":
    asyncio.run(main())

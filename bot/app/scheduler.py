"""Background scheduler for daily engagement notifications."""
import logging
from datetime import datetime
import asyncio
from aiogram import Bot

from app.services.api_client import api

logger = logging.getLogger(__name__)

async def process_daily_notifications(bot: Bot):
    """Job to send daily review reminders based on user's preferred time."""
    logger.info("Running hourly notification job...")
    try:
        users_with_due = await api.get_all_due_reviews()
        current_hour = datetime.now().hour
        
        # Send review reminders
        for u in users_with_due:
            user_id = u["telegram_id"]
            user_time = u.get("notification_time", "10:00")
            
            # Extract preferred hour from '10:00'
            try:
                preferred_hour = int(user_time.split(":")[0])
            except (ValueError, AttributeError):
                preferred_hour = 10
                
            if current_hour != preferred_hour:
                continue
                
            msg = "📚 You have poems to review! Check /review"
            
            try:
                await bot.send_message(user_id, msg)
                # Keep requests within telegram limits
                await asyncio.sleep(0.1) 
            except Exception as e:
                logger.error(f"Failed to send review push to {user_id}: {e}")
                
    except Exception as e:
        logger.error(f"Failed to run hourly notifications: {e}")

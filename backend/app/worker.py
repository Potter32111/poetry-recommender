import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.parser import parser

logger = logging.getLogger(__name__)

# List of URLs to parse periodically as part of the auto-growing library
INITIAL_TARGET_URLS = [
    "https://stihi.ru/2004/08/25-240", # Sample existing poem link
    "https://stihi.ru/2006/04/23-149", # Pushkin or Lermontov
]

async def crawl_and_parse():
    """Background task to fetch and process new poems."""
    logger.info("Starting background crawl for new poems...")
    # In a fully fleshed out system, we would:
    # 1. Fetch an index page (e.g., top 100 poems)
    # 2. Extract links
    # 3. Filter ones we already processed
    # 4. Call parser.process_url(link)
    
    # For now, we simulate crawling by just processing a static list or a known author archive.
    urls_to_process = INITIAL_TARGET_URLS
    
    for url in urls_to_process:
        try:
            poem = await parser.process_url(url)
            if poem:
                logger.info(f"Successfully auto-parsed and embedded '{poem.title}'")
        except Exception as e:
            logger.error(f"Error processing {url} during crawl: {e}")
            
    logger.info("Finished background crawl cycle.")

scheduler = AsyncIOScheduler()

def start_worker():
    """Initializes the background worker for auto-scraping."""
    logger.info("Initializing background parsing worker...")
    # Run once an hour for example, or everyday
    scheduler.add_job(crawl_and_parse, 'interval', hours=24)
    scheduler.start()

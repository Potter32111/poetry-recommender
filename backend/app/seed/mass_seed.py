import asyncio
import re
import aiohttp
import logging
import random
from app.services.parser import parser

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# lib.ru poetry sources
LITRA_SOURCES = [
    "PUSHKIN", "LERMONTOW", "ESENIN", "TIUTCHEW", "FET", "BLOK", 
    "AHMATOWA", "NEKRASOW", "BUNIN", "PASTERNAK", "GUMILEW"
]

POEZIQ_SOURCES = [
    "MAQROWSKIJ", "CWETAEWA", "MANDELSHTAM", "OKUDZHAWA", "WYSOCKIJ", 
    "TWARDOWSKIJ", "ALIGER_M", "ASADOW", "WOZNESENSKIJ", "DRUNINA", "ZABOLOCKIJ"
]

async def extract_links_libru(base_url: str, author_slug: str, limit: int = 150):
    url = f"{base_url}{author_slug}/"
    html = await parser.fetch_html(url)
    if not html: return []
    
    # regex for lib.ru links: href="...txt" or href="...html"
    pattern = r'href="?([^" >]+\.(?:txt|html))"?'
    matches = re.findall(pattern, html, re.IGNORECASE)
    
    links = []
    exclude = ["about.txt", "index.html", "index.txt", "info.txt"]
    for m in matches:
        if m.lower() not in exclude and not m.startswith("http"):
            links.append(f"{url}{m}")
            
    return list(set(links))[:limit]

async def mass_seed():
    logger.info("Starting CORRECTED LIB.RU POWER SEED...")
    all_links = []
    
    # 1. Classics from LITRA
    for author in LITRA_SOURCES:
        try:
            links = await extract_links_libru("http://lib.ru/LITRA/", author, limit=80)
            all_links.extend(links)
            logger.info(f"LITRA: Found {len(links)} links for {author}")
        except Exception as e:
            logger.error(f"Error getting LITRA links for {author}: {e}")

    # 2. Moderns from POEZIQ
    for author in POEZIQ_SOURCES:
        try:
            links = await extract_links_libru("http://lib.ru/POEZIQ/", author, limit=80)
            all_links.extend(links)
            logger.info(f"POEZIQ: Found {len(links)} links for {author}")
        except Exception as e:
            logger.error(f"Error getting POEZIQ links for {author}: {e}")

    random.shuffle(all_links)
    logger.info(f"Total unique links gathered: {len(all_links)}")
    
    success_count = 0
    chunk_size = 5
    for i in range(0, len(all_links), chunk_size):
        chunk = all_links[i:i + chunk_size]
        tasks = [parser.process_url(url) for url in chunk]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results:
            if res and not isinstance(res, Exception):
                success_count += 1
                
        logger.info(f"Progress: {min(i + chunk_size, len(all_links))}/{len(all_links)}... (Seed Success: {success_count})")
        
        if success_count % 20 == 0:
             from app.database import async_session
             from app.models.poem import Poem
             from sqlalchemy import select, func
             async with async_session() as s: 
                 current_count = (await s.execute(select(func.count(Poem.id)))).scalar()
                 if current_count >= 1000:
                     logger.info(f"Target reached: {current_count} poems in DB. Success!")
                     return
        
        await asyncio.sleep(0.3)

    logger.info(f"MASS SEED COMPLETE. Added {success_count} poems.")
    await parser.close_session()

if __name__ == "__main__":
    asyncio.run(mass_seed())

import asyncio
import re
import aiohttp
import logging
import random
from app.services.parser import parser

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# lib.ru/LITRARU/ author directories
AUTHORS_LIB_RU = [
    "PUSHKIN", "LERMONTOW", "ESENIN", "TIUTCHEW", "FET", "BLOK", 
    "AHMATOWA", "MAQROWSKIJ", "CWETAEWA", "NEKRASOW", "BUNIN", "PASTERNAK",
    "MANDELSHTAM", "GUMILEW", "OKUDZHAWA", "WYSOCKIJ", "TWARDOWSKIJ"
]

async def extract_links_libru(author_slug: str, limit: int = 150):
    url = f"http://lib.ru/LITRARU/{author_slug}/"
    html = await parser.fetch_html(url)
    if not html: return []
    
    # regex for lib.ru links: href="...txt" or href="...html"
    # we filter out common non-poem files
    pattern = r'href="([^"]+\.(?:txt|html))"'
    matches = re.findall(pattern, html)
    
    links = []
    exclude = ["about.txt", "index.html", "index.txt", "info.txt"]
    for m in matches:
        if m.lower() not in exclude and not m.startswith("http"):
            links.append(f"{url}{m}")
            
    return list(set(links))[:limit]

async def mass_seed():
    logger.info("Starting LIB.RU POWER SEED (Moshkow's Library)...")
    all_links = []
    
    for author in AUTHORS_LIB_RU:
        try:
            links = await extract_links_libru(author, limit=100)
            all_links.extend(links)
            logger.info(f"LIB.RU: Found {len(links)} links for {author}")
        except Exception as e:
            logger.error(f"Error getting LIBRU links for {author}: {e}")
    
    # Also keep some Stihi.ru as backup
    backup_authors = ["pushkin", "lermontov", "esenin1", "blok"]
    for author in backup_authors:
        try:
             url = f"https://stihi.ru/avtor/{author}"
             html = await parser.fetch_html(url)
             if html:
                 pattern = r'href="(/[0-9]{4}/[0-9]{2}/[0-9]{2}/[0-9]+)"'
                 links = [f"https://stihi.ru{l}" for l in re.findall(pattern, html)[:50]]
                 all_links.extend(links)
        except: pass

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
             # Regular check to stop at 1000
             from app.database import async_session
             from app.models.poem import Poem
             from sqlalchemy import select, func
             async with async_session() as s: 
                 current_count = (await s.execute(select(func.count(Poem.id)))).scalar()
                 if current_count >= 1000:
                     logger.info(f"Target reached: {current_count} poems in DB. Success!")
                     return
        
        await asyncio.sleep(0.5)

    logger.info(f"MASS SEED COMPLETE. Added {success_count} poems.")
    await parser.close_session()

if __name__ == "__main__":
    asyncio.run(mass_seed())

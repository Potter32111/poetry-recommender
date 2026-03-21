import asyncio
import re
import aiohttp
import logging
import random
from app.services.parser import parser

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Expanded list of authors on stihi.ru
AUTHORS_RU = [
    "pushkin", "lermontov", "esenin1", "tyutchev", "fet1", "blok", "akhmatova", 
    "mayakovsky", "tsvetayeva", "mandelshtam", "brodsky", "tvardovsky", 
    "pasternak", "nekrasov1", "bunin", "gumilev", "okudzhava", "vysotsky"
]

# PoemHunter authors for diversity
AUTHORS_EN = [
    "william-shakespeare", "robert-frost", "maya-angelou", "edgar-allan-poe",
    "emily-dickinson", "walt-whitman", "langston-hughes", "john-keats",
    "sylvia-plath", "william-butler-yeats", "oscar-wilde", "rudyard-kipling"
]

async def extract_links_ru(author_slug: str, limit: int = 100):
    url = f"https://stihi.ru/avtor/{author_slug}"
    html = await parser.fetch_html(url)
    if not html: return []
    
    # regex for stihi.ru poem links: /YYYY/MM/DD/ID - sometimes with or without trailing quote
    pattern = r'href="(/[0-9]{4}/[0-9]{2}/[0-9]{2}/[0-9]+)"'
    links = re.findall(pattern, html)
    return [f"https://stihi.ru{l}" for l in list(set(links))[:limit]]

async def extract_links_en(author_slug: str, limit: int = 50):
    url = f"https://www.poemhunter.com/{author_slug}/poems/"
    html = await parser.fetch_html(url)
    if not html: return []
    
    # regex for poemhunter: href="/poem/..."
    pattern = r'href="(/poem/[^/"]+/)"'
    links = re.findall(pattern, html)
    return [f"https://www.poemhunter.com{l}" for l in list(set(links))[:limit]]

async def mass_seed():
    logger.info("Starting AGGRESSIVE MASS SEED of 1000+ poems...")
    all_links = []
    
    for author in AUTHORS_RU:
        try:
            links = await extract_links_ru(author, limit=100)
            all_links.extend(links)
            logger.info(f"RU: Found {len(links)} poems for {author}")
            await asyncio.sleep(1) # Be polite
        except Exception as e:
            logger.error(f"Error getting RU links for {author}: {e}")

    for author in AUTHORS_EN:
        try:
            links = await extract_links_en(author, limit=50)
            all_links.extend(links)
            logger.info(f"EN: Found {len(links)} poems for {author}")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error getting EN links for {author}: {e}")

    random.shuffle(all_links)
    logger.info(f"Total unique links gathered: {len(all_links)}")
    
    success_count = 0
    chunk_size = 3 # Smaller chunks to be safer
    for i in range(0, len(all_links), chunk_size):
        chunk = all_links[i:i + chunk_size]
        tasks = [parser.process_url(url) for url in chunk]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results:
            if res and not isinstance(res, Exception):
                success_count += 1
                
        logger.info(f"Progress: {min(i + chunk_size, len(all_links))}/{len(all_links)}... (Seed Success: {success_count})")
        await asyncio.sleep(1.5)
        
        if i % 50 == 0 and i > 0:
             # Check database count to avoid duplicates or overfilling
             from app.database import async_session
             from app.models.poem import Poem
             from sqlalchemy import select, func
             async with async_session() as s: 
                 current_count = (await s.execute(select(func.count(Poem.id)))).scalar()
                 if current_count >= 1000:
                     logger.info(f"Database reached {current_count} poems. Finishing.")
                     return

    logger.info(f"MASS SEED COMPLETE. Total added in this run: {success_count} poems.")
    await parser.close_session()

if __name__ == "__main__":
    asyncio.run(mass_seed())

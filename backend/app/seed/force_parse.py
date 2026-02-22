import asyncio
import logging
from app.services.parser import parser

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

URLs = [
    "https://stihi.ru/2014/02/10/5836", # Пушкин - Я вас любил
    "https://stihi.ru/2012/10/29/7391", # Есенин - Письмо к женщине
    "https://stihi.ru/2008/04/10/2486", # Блок - Не жалею, не зову, не плачу
    "https://stihi.ru/2009/11/04/3200", # Тютчев - Умом Россию не понять
    "https://stihi.ru/2015/09/25/6873", # Бродский - Ночь
    "https://stihi.ru/2012/08/17/3847", # Лермонтов - Парус
    "https://stihi.ru/2011/03/09/8816", # Ахматова - Сжала руки под темной вуалью...
    "https://stihi.ru/2010/01/21/5302", # Маяковский - Послушайте!
    "https://stihi.ru/2003/11/07-29",   # Цветаева - Мне нравится, что вы больны не мной 
]

async def force_parse():
    logger.info("Starting FORCE PARSE of beautiful classic poems...")
    success_count = 0
    
    for url in URLs:
        try:
            logger.info(f"Attempting to parse: {url}")
            poem = await parser.process_url(url)
            if poem:
                success_count += 1
                logger.info(f"SUCCESS: Loaded '{poem.title}' by {poem.author}")
            else:
                logger.warning(f"FAILED: Could not extract poem from {url}")
        except Exception as e:
            logger.error(f"Error parsing {url}: {e}")
            
        # small delay to be polite to the server
        await asyncio.sleep(2)
        
    logger.info(f"FORCE PARSE COMPLETE. Successfully added {success_count}/{len(URLs)} poems.")

    # cleanup aiohttp session
    await parser.close_session()

if __name__ == "__main__":
    asyncio.run(force_parse())

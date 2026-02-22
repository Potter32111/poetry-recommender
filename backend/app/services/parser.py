import asyncio
import aiohttp
import logging
from typing import List, Optional

import urllib.parse
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

from app.database import async_session
from app.models.poem import Poem
from app.services.ml import ml_service

logger = logging.getLogger(__name__)

class PoemParser:
    """Async parser for fetching and saving poems."""
    
    def __init__(self):
        # We will set the session lazily
        self.session: Optional[aiohttp.ClientSession] = None

    async def init_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def fetch_html(self, url: str) -> Optional[str]:
        await self.init_session()
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                logger.error(f"Failed to fetch {url}: HTTP {response.status}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
        return None

    async def parse_poem_page(self, html: str, url: str = "") -> Optional[dict]:
        """
        Parses exactly one poem from an HTML string based on the site.
        """
        if not html:
            return None
            
        soup = BeautifulSoup(html, "html.parser")
        
        # Default initialization
        title = "Untitled"
        author = "Unknown"
        text = ""
        language = "ru" if "stihi.ru" in url or "rustih.ru" in url else "en"
        
        if "stihi.ru" in url:
            # Stihi.ru parsing logic
            title_node = soup.find("h1")
            author_node = soup.find("div", class_="titleauthor")
            text_node = soup.find("div", class_="text")
            
            if title_node: title = title_node.get_text(strip=True)
            if author_node:
                a_tag = author_node.find("a")
                if a_tag: author = a_tag.get_text(strip=True)
            if text_node: text = text_node.get_text(separator="\n", strip=True)
            
        elif "poemhunter.com" in url:
            # Poemhunter.com parsing logic
            title_node = soup.find("h1", class_="title")
            author_node = soup.find("a", class_="poet")
            text_node = soup.find("p", class_="poem-body")
            
            if title_node: title = title_node.get_text(strip=True)
            if author_node: author = author_node.get_text(strip=True)
            if text_node: text = text_node.get_text(separator="\n", strip=True)
        else:
            # Fallback for generic sites
            title_node = soup.find("h1")
            if title_node: title = title_node.get_text(strip=True)
            
            paragraphs = soup.find_all("p")
            text = "\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 0)
            
        if len(text) < 20: # too short, probably not a poem or failed parse
            return None
            
        lines_count = len(text.strip().split("\n"))
        difficulty = 1.0 + min(lines_count / 10.0, 4.0) # naive difficulty based on length
            
        return {
            "title": title,
            "author": author,
            "text": text,
            "language": language,
            "difficulty": difficulty,
            "lines_count": lines_count
        }

    async def process_url(self, url: str) -> Optional[Poem]:
        """Orchestrates parsing the URL, generating an embedding, and saving to database."""
        logger.info(f"Processing URL: {url}")
        html = await self.fetch_html(url)
        data = await self.parse_poem_page(html, url)
        
        if data:
            logger.info(f"Generating embedding for '{data['title']}'...")
            embedding = await ml_service.generate_embedding(data["text"])
            
            async with async_session() as db:
                poem = Poem(
                    title=data["title"],
                    author=data["author"],
                    text=data["text"],
                    language=data["language"],
                    difficulty=data["difficulty"],
                    lines_count=data["lines_count"],
                    embedding=embedding
                )
                db.add(poem)
                await db.commit()
                await db.refresh(poem)
            
            logger.info(f"Successfully saved poem '{poem.title}'.")
            return poem
        return None
        
    async def search_and_parse(self, query: str, limit: int = 3) -> List[Poem]:
        """Performs a real-time internet search using Yandex Cloud Search API v2."""
        import random
        logger.info(f"Initiating real-time Yandex search for query: '{query}'")
        
        import os
        API_KEY = os.getenv('YANDEX_SEARCH_API_KEY')
        FOLDER_ID = os.getenv('YANDEX_FOLDER_ID')
        if not API_KEY:
            logger.error('Yandex API_KEY missing')
            return []
        
        # Enrich the query with poetic variations
        ru_modifiers = ["Ð³Ð»ÑƒÐ±Ð¾ÐºÐ¸Ð¹ ÑÐ¼Ñ‹ÑÐ»", "Ð¼ÐµÑ‚Ð°Ñ„Ð¾Ñ€Ð°", "Ñ„Ð¸Ð»Ð¾ÑÐ¾Ñ„Ð¸Ñ", "Ð´ÑƒÑˆÐ°", "Ð²Ð´Ð¾Ñ…Ð½Ð¾Ð²ÐµÐ½Ð¸Ðµ", "Ð»Ð¸Ñ€Ð¸ÐºÐ°", "ÐºÑ€Ð°ÑÐ¸Ð²Ð¾"]
        en_modifiers = ["deep meaning", "metaphor", "philosophy", "soul", "inspiration", "lyrical", "beautiful"]
        
        is_ru = any('\u0400' <= c <= '\u04FF' for c in query)
        
        if len(query.split()) <= 2:
             modifier = random.choice(ru_modifiers) if is_ru else random.choice(en_modifiers)
             enhanced_query = f"{query} {modifier}"
             logger.info(f"Enhanced short query '{query}' -> '{enhanced_query}'")
        else:
             enhanced_query = query
        
        search_query = f"{enhanced_query} ÑÑ‚Ð¸Ñ… site:stihi.ru" if is_ru else f"{enhanced_query} poem site:poemhunter.com"
        url = "https://searchapi.api.cloud.yandex.net/v2/web/search"
        
        payload = {
            "query": {
                "searchType": "SEARCH_TYPE_RU",
                "queryText": search_query
            },
            "folderId": FOLDER_ID
        }
        
        headers = {
            "Authorization": f"Api-Key {API_KEY}",
            "Content-Type": "application/json"
        }
        
        parsed_poems = []
        try:
            await self.init_session()
            async with self.session.post(url, headers=headers, json=payload, timeout=15) as resp:
                if resp.status != 200:
                    error_body = await resp.text()
                    logger.error(f"Yandex API error {resp.status}: {error_body}")
                    return []
                
                data = await resp.json()
                
                # Extract base64 result
                raw_xml = None
                if "rawData" in data:
                    raw_xml = base64.b64decode(data["rawData"]).decode("utf-8")
                elif "response" in data:
                     raw_xml = base64.b64decode(data["response"]).decode("utf-8")
                else:
                    for k, v in data.items():
                        if isinstance(v, str) and len(v) > 100:
                            try:
                                decoded = base64.b64decode(v).decode("utf-8")
                                if "<?xml" in decoded or "<yandexsearch" in decoded:
                                    raw_xml = decoded
                                    break
                            except: continue

                if not raw_xml:
                    logger.warning("Could not find XML results in Yandex response.")
                    return []
                
                root = ET.fromstring(raw_xml)
                result_links = [u.text for u in root.findall(".//url")][:limit]
                
                if not result_links:
                    logger.warning(f"No internet search results for: '{search_query}'")
                    return []
                    
                logger.info(f"Found {len(result_links)} URLs. Attempting to parse them.")
                for link in result_links:
                    poem = await self.process_url(link)
                    if poem:
                        parsed_poems.append(poem)
                        
            if not parsed_poems:
                logger.warning("No URLs extracted from Yandex response.")
            
            return parsed_poems
            
        except asyncio.TimeoutError:
            logger.error("Yandex API request timed out.")
            return []
        except Exception as e:
            logger.error(f"Error during Yandex search: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
        finally:
            if self.session and not self.session.closed:
                await self.session.close()
                self.session = None
        
parser = PoemParser()


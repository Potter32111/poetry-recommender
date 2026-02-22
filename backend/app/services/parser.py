import asyncio
import logging
from typing import List, Optional

import aiohttp
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
                "User-Agent": "Mozilla/5.0 (PoetryRecSys Bot; +http://example.com/bot)"
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

    async def parse_poem_page(self, html: str) -> Optional[dict]:
        """
        Parses exactly one poem from an HTML string.
        Adjust the selectors depending on the target website.
        """
        if not html:
            return None
            
        soup = BeautifulSoup(html, "html.parser")
        
        # Search for Title
        title_element = soup.find("h1")
        if not title_element:
            return None
        title = title_element.get_text(strip=True)
        
        # Search for Author
        author = "Неизвестный"
        
        # Search for Poem Text
        text_element = soup.find("div", class_="poem-text")
        if not text_element:
            paragraphs = soup.find_all("p")
            text = "\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 0)
        else:
            text = text_element.get_text(separator="\n", strip=True)
            
        if len(text) < 10:
            return None
            
        return {
            "title": title,
            "author": author,
            "text": text,
            "language": "ru",
            "difficulty": 3,
            "lines_count": len(text.strip().split("\n"))
        }

    async def process_url(self, url: str) -> Optional[Poem]:
        """Orchestrates parsing the URL, generating an embedding, and saving to database."""
        html = await self.fetch_html(url)
        data = await self.parse_poem_page(html)
        
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
        
parser = PoemParser()

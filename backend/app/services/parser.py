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
        
parser = PoemParser()

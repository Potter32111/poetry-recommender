import asyncio
import logging
from sqlalchemy import select
from app.database import async_session
from app.models.poem import Poem
from app.services.ml import ml_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_embeddings():
    """Generates embeddings for all poems that don't have them."""
    async with async_session() as db:
        # Fetch poems missing embeddings
        result = await db.execute(select(Poem).where(Poem.embedding.is_(None)))
        poems = result.scalars().all()
        
        if not poems:
            logger.info("No poems missing embeddings found.")
            return

        logger.info(f"Found {len(poems)} poems to process.")
        
        for poem in poems:
            logger.info(f"Generating embedding for '{poem.title}'...")
            embedding = await ml_service.generate_embedding(poem.text)
            poem.embedding = embedding
            # Update difficulty if needed or other metadata
            
        await db.commit()
        logger.info("Successfully updated all poems with embeddings.")

if __name__ == "__main__":
    asyncio.run(seed_embeddings())

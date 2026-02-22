import asyncio
import logging

from sqlalchemy import select

from app.database import async_session
from app.models.poem import Poem
from app.services.ml import ml_service

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def backfill_embeddings():
    """Iterate through all poems in the DB that lack an embedding and generate one."""
    logger.info("Connecting to the database to backfill embeddings...")
    
    async with async_session() as db:
        # We find poems where embedding is NULL.
        # pgvector columns can be checked with is_(None)
        result = await db.execute(select(Poem).where(Poem.embedding.is_(None)))
        poems_to_update = result.scalars().all()
        
        if not poems_to_update:
            logger.info("All poems already have embeddings. Nothing to do.")
            return

        logger.info(f"Found {len(poems_to_update)} poems without embeddings. Generating...")
        
        # Load model once before the loop to save time
        await asyncio.to_thread(ml_service.load_model)

        for poem in poems_to_update:
            logger.info(f"Generating embedding for '{poem.title}' by {poem.author}...")
            # We construct a rich text string for the embedding context if we want, 
            # but for now, just the text is fine, maybe prepending the themes.
            themes_str = ", ".join(poem.themes) if poem.themes else "general poetry"
            context_text = f"Title: {poem.title}\nAuthor: {poem.author}\nLanguage: {poem.language}\nThemes: {themes_str}\n\n{poem.text}"
            
            embedding = await ml_service.generate_embedding(context_text)
            poem.embedding = embedding
            
            # Commit after each one or batch commit? Batch is better but they are small.
            # We'll just flush/commit at the end or every 10
            
        logger.info("Committing all updated embeddings to the database...")
        await db.commit()
        logger.info("Backfill complete!")

if __name__ == "__main__":
    asyncio.run(backfill_embeddings())

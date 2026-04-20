"""Seed script for curated collections."""

import asyncio
import logging

from sqlalchemy import select

from app.database import async_session
from app.models.collection import Collection, CollectionPoem
from app.models.poem import Poem
from app.seed.collections_data import COLLECTIONS

logger = logging.getLogger(__name__)


def _matches_filter(poem: Poem, filt: dict) -> bool:
    """Check if a poem matches the collection filter criteria."""
    if "authors" in filt and not any(
        kw.lower() in poem.author.lower() for kw in filt["authors"]
    ):
        return False
    if "themes" in filt:
        poem_themes = [t.lower() for t in (poem.themes or [])]
        if not any(kw.lower() in " ".join(poem_themes) for kw in filt["themes"]):
            return False
    if "era" in filt and poem.era != filt["era"]:
        return False
    return not ("max_lines" in filt and poem.lines_count > filt["max_lines"])


async def seed_collections() -> None:
    """Seed official collections based on filter rules. Idempotent."""
    async with async_session() as db:
        # Load all poems
        result = await db.execute(select(Poem))
        all_poems = list(result.scalars().all())
        logger.info("Seeding collections against %d poems", len(all_poems))

        for col_data in COLLECTIONS:
            slug = col_data["slug"]
            # Check if collection already exists
            existing = await db.execute(
                select(Collection).where(Collection.slug == slug)
            )
            col = existing.scalar_one_or_none()
            if col:
                logger.info("Collection '%s' already exists, skipping", slug)
                continue

            col = Collection(
                slug=slug,
                title_ru=col_data["title_ru"],
                title_en=col_data["title_en"],
                description_ru=col_data["description_ru"],
                description_en=col_data["description_en"],
                cover_emoji=col_data["cover_emoji"],
                is_official=True,
            )
            db.add(col)
            await db.flush()

            filt = col_data["filter"]
            matched = [p for p in all_poems if _matches_filter(p, filt)]
            for pos, poem in enumerate(matched):
                db.add(CollectionPoem(
                    collection_id=col.id,
                    poem_id=poem.id,
                    position=pos,
                ))
            logger.info(
                "Created collection '%s' with %d poems", slug, len(matched)
            )

        await db.commit()
        logger.info("Collection seeding complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_collections())

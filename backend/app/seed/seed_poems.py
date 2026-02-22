"""Seed the database with classic poems."""

import asyncio

from sqlalchemy import select, func

from app.database import engine, async_session
from app.models.user import Base
from app.models.poem import Poem
from app.seed.poems_data import POEMS


async def seed_poems() -> None:
    """Insert poems into the database if not already present."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        result = await session.execute(select(func.count(Poem.id)))
        count = result.scalar() or 0

        if count > 0:
            print(f"Database already has {count} poems, skipping seed.")
            return

        for poem_data in POEMS:
            text = poem_data["text"]
            poem = Poem(
                title=poem_data["title"],
                author=poem_data["author"],
                text=text,
                language=poem_data["language"],
                difficulty=poem_data["difficulty"],
                themes=poem_data["themes"],
                era=poem_data.get("era"),
                lines_count=len(text.strip().split("\n")),
            )
            session.add(poem)

        await session.commit()
        print(f"Seeded {len(POEMS)} poems into the database.")


if __name__ == "__main__":
    asyncio.run(seed_poems())

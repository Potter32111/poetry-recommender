"""Collections API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.collection import Collection, CollectionPoem
from app.schemas.collection import CollectionBrief, CollectionFull
from app.schemas.poem import PoemResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("/", response_model=list[CollectionBrief])
async def list_collections(db: AsyncSession = Depends(get_db)):
    """List all official collections with poem counts."""
    result = await db.execute(
        select(Collection).where(Collection.is_official.is_(True))
    )
    collections = list(result.scalars().all())
    items = []
    for col in collections:
        count_result = await db.execute(
            select(func.count(CollectionPoem.id)).where(
                CollectionPoem.collection_id == col.id
            )
        )
        count = count_result.scalar() or 0
        items.append(
            CollectionBrief(
                id=col.id,
                slug=col.slug,
                title_ru=col.title_ru,
                title_en=col.title_en,
                description_ru=col.description_ru,
                description_en=col.description_en,
                cover_emoji=col.cover_emoji,
                is_official=col.is_official,
                poem_count=count,
            )
        )
    return items


@router.get("/{slug}", response_model=CollectionFull)
async def get_collection(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a collection with all its poems."""
    result = await db.execute(select(Collection).where(Collection.slug == slug))
    col = result.scalar_one_or_none()
    if not col:
        raise HTTPException(status_code=404, detail="Collection not found")
    # Load poems via join table
    poems_result = await db.execute(
        select(CollectionPoem)
        .where(CollectionPoem.collection_id == col.id)
        .order_by(CollectionPoem.position)
    )
    collection_poems = list(poems_result.scalars().all())
    poems = []
    for cp in collection_poems:
        await db.refresh(cp, ["poem"])
        if cp.poem:
            poems.append(
                PoemResponse(
                    id=cp.poem.id,
                    title=cp.poem.title,
                    author=cp.poem.author,
                    text=cp.poem.text,
                    language=cp.poem.language,
                    difficulty=cp.poem.difficulty,
                    themes=cp.poem.themes or [],
                    era=cp.poem.era,
                    lines_count=cp.poem.lines_count,
                )
            )
    return CollectionFull(
        id=col.id,
        slug=col.slug,
        title_ru=col.title_ru,
        title_en=col.title_en,
        description_ru=col.description_ru,
        description_en=col.description_en,
        cover_emoji=col.cover_emoji,
        is_official=col.is_official,
        poems=poems,
    )

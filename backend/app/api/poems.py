"""Poem API endpoints."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.poem import Poem
from app.schemas.poem import PoemCreate, PoemResponse, PoemBrief, ParseRequest
from app.services.parser import parser

router = APIRouter(prefix="/poems", tags=["poems"])


@router.get("/", response_model=list[PoemBrief])
async def list_poems(
    language: str | None = Query(None, description="Filter by language: en, ru"),
    author: str | None = Query(None, description="Filter by author"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List poems with optional filtering."""
    query = select(Poem)
    if language:
        query = query.where(Poem.language == language)
    if author:
        query = query.where(Poem.author.ilike(f"%{author}%"))
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/count")
async def count_poems(db: AsyncSession = Depends(get_db)):
    """Get total poem count."""
    result = await db.execute(select(func.count(Poem.id)))
    return {"count": result.scalar()}


@router.get("/{poem_id}", response_model=PoemResponse)
async def get_poem(poem_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get poem by ID."""
    query = select(Poem).where(Poem.id == poem_id)
    result = await db.execute(query)
    poem = result.scalar_one_or_none()
    if not poem:
        raise HTTPException(status_code=404, detail="Poem not found")
    return poem


@router.post("/", response_model=PoemResponse, status_code=201)
async def create_poem(data: PoemCreate, db: AsyncSession = Depends(get_db)):
    """Add a new poem."""
    poem = Poem(
        title=data.title,
        author=data.author,
        text=data.text,
        language=data.language,
        difficulty=data.difficulty,
        themes=data.themes,
        era=data.era,
        lines_count=len(data.text.strip().split("\n")),
    )
    db.add(poem)
    await db.commit()
    await db.refresh(poem)
    return poem

@router.get("/top-authors")
async def top_authors(
    limit: int = Query(6, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Return the most-popular authors by poem count."""
    result = await db.execute(
        select(Poem.author, func.count(Poem.id).label("poem_count"))
        .group_by(Poem.author)
        .order_by(func.count(Poem.id).desc())
        .limit(limit)
    )
    return [{"author": row.author, "poem_count": row.poem_count} for row in result.all()]


@router.post("/parse", response_model=PoemResponse, status_code=201)
async def parse_new_poem(request: ParseRequest):
    """Parse a poem from a given URL and add it to the database."""
    poem = await parser.process_url(request.url)
    if not poem:
        raise HTTPException(status_code=400, detail="Failed to parse poem from the provided URL. Ensure it is a valid link to a poem on a supported site (e.g. stihi.ru).")
    return poem

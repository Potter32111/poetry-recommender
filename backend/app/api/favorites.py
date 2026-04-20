"""Favorites API endpoints."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.favorite import Favorite
from app.models.poem import Poem
from app.models.user import User
from app.schemas.favorite import FavoriteResponse, IsFavoriteResponse
from app.schemas.poem import PoemResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/favorites", tags=["favorites"])


async def _get_user(telegram_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{telegram_id}/{poem_id}", response_model=FavoriteResponse)
async def add_favorite(
    telegram_id: int,
    poem_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Add a poem to favorites. Idempotent: returns existing if already saved."""
    user = await _get_user(telegram_id, db)

    existing = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user.id, Favorite.poem_id == poem_id
        )
    )
    fav = existing.scalar_one_or_none()
    if fav:
        return fav

    poem_check = await db.execute(select(Poem).where(Poem.id == poem_id))
    if not poem_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Poem not found")

    fav = Favorite(user_id=user.id, poem_id=poem_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav


@router.delete("/{telegram_id}/{poem_id}", status_code=204)
async def remove_favorite(
    telegram_id: int,
    poem_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Remove a poem from favorites."""
    user = await _get_user(telegram_id, db)
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user.id, Favorite.poem_id == poem_id
        )
    )
    fav = result.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    await db.delete(fav)
    await db.commit()


@router.get("/{telegram_id}", response_model=list[PoemResponse])
async def list_favorites(
    telegram_id: int,
    db: AsyncSession = Depends(get_db),
):
    """List all favorite poems for a user."""
    user = await _get_user(telegram_id, db)
    result = await db.execute(
        select(Favorite)
        .where(Favorite.user_id == user.id)
        .order_by(Favorite.created_at.desc())
    )
    favs = list(result.scalars().all())
    poems = []
    for fav in favs:
        await db.refresh(fav, ["poem"])
        if fav.poem:
            poems.append(fav.poem)
    return poems


@router.get("/{telegram_id}/{poem_id}/check", response_model=IsFavoriteResponse)
async def check_favorite(
    telegram_id: int,
    poem_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Check if a poem is in user's favorites."""
    user = await _get_user(telegram_id, db)
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user.id, Favorite.poem_id == poem_id
        )
    )
    fav = result.scalar_one_or_none()
    return IsFavoriteResponse(is_favorite=fav is not None)

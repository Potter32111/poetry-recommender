"""User API endpoints."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.database import get_db
from app.models.user import User
from app.models.memorization import Memorization
from app.schemas.user import UserCreate, UserUpdate, UserResponse, LeaderboardUser

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_or_get_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user or return existing by telegram_id."""
    query = select(User).where(User.telegram_id == data.telegram_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user:
        return user

    user = User(
        telegram_id=data.telegram_id,
        username=data.username,
        first_name=data.first_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/leaderboard", response_model=List[LeaderboardUser])
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    """Get top 10 users for the leaderboard."""
    query = select(User).order_by(User.level.desc(), User.xp.desc()).limit(10)
    result = await db.execute(query)
    users = result.scalars().all()
    return list(users)


@router.get("/all", response_model=List[LeaderboardUser])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    """Get all users (for scheduler notifications)."""
    query = select(User).order_by(User.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{telegram_id}", response_model=UserResponse)
async def get_user(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """Get user by Telegram ID."""
    query = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{telegram_id}", response_model=UserResponse)
async def update_user(
    telegram_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)
):
    """Update user preferences."""
    query = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{telegram_id}/progress", status_code=200)
async def reset_user_progress(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """Delete all memorization rows and reset XP/level/streak for a user."""
    query = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.execute(
        delete(Memorization).where(Memorization.user_id == user.id)
    )

    user.xp = 0
    user.level = 1
    user.streak = 0
    user.last_activity_date = None

    await db.commit()
    await db.refresh(user)
    return {"status": "ok"}

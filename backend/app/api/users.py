"""User API endpoints."""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse

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

import uuid
from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None


class UserUpdate(BaseModel):
    language_pref: str | None = None
    preferences: dict | None = None
    ui_language: str | None = None
    notification_time: str | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    telegram_id: int
    username: str | None
    first_name: str | None
    language_pref: str
    preferences: dict
    xp: int
    level: int
    streak: int
    ui_language: str
    notification_time: str
    streak_freezes_available: int = 1
    created_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardUser(BaseModel):
    telegram_id: int
    first_name: str | None
    level: int
    xp: int
    streak: int

    model_config = {"from_attributes": True}

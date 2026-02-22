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


class UserResponse(BaseModel):
    id: uuid.UUID
    telegram_id: int
    username: str | None
    first_name: str | None
    language_pref: str
    preferences: dict
    created_at: datetime

    model_config = {"from_attributes": True}

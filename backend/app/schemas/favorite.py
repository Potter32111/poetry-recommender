"""Favorite schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class FavoriteResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    poem_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class IsFavoriteResponse(BaseModel):
    is_favorite: bool

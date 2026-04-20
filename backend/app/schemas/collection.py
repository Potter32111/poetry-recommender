"""Collection schemas."""

import uuid

from pydantic import BaseModel

from app.schemas.poem import PoemResponse


class CollectionBrief(BaseModel):
    id: uuid.UUID
    slug: str
    title_ru: str
    title_en: str
    description_ru: str
    description_en: str
    cover_emoji: str
    is_official: bool
    poem_count: int = 0

    model_config = {"from_attributes": True}


class CollectionFull(BaseModel):
    id: uuid.UUID
    slug: str
    title_ru: str
    title_en: str
    description_ru: str
    description_en: str
    cover_emoji: str
    is_official: bool
    poems: list[PoemResponse] = []

    model_config = {"from_attributes": True}

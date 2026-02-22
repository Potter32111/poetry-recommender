import uuid

from pydantic import BaseModel


class PoemCreate(BaseModel):
    title: str
    author: str
    text: str
    language: str = "en"
    difficulty: int = 3
    themes: list[str] = []
    era: str | None = None


class PoemResponse(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    text: str
    language: str
    difficulty: int
    themes: list[str]
    era: str | None
    lines_count: int

    model_config = {"from_attributes": True}


class PoemBrief(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    language: str
    difficulty: int
    lines_count: int

    model_config = {"from_attributes": True}

import uuid

from pydantic import BaseModel


class PoemCreate(BaseModel):
    title: str
    author: str
    text: str
    language: str = "en"
    difficulty: float = 3.0
    themes: list[str] = []
    era: str | None = None


class PoemResponse(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    text: str
    language: str
    difficulty: float
    themes: list[str]
    era: str | None
    lines_count: int

    model_config = {"from_attributes": True}


class PoemBrief(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    language: str
    difficulty: float
    lines_count: int

    model_config = {"from_attributes": True}

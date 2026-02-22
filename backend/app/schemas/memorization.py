import uuid
from datetime import datetime

from pydantic import BaseModel


class MemorizationCreate(BaseModel):
    user_id: uuid.UUID
    poem_id: uuid.UUID


class ReviewRequest(BaseModel):
    score: int  # 0-5, SM-2 quality rating


class MemorizationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    poem_id: uuid.UUID
    status: str
    ease_factor: float
    interval_days: int
    repetitions: int
    next_review_at: datetime | None
    last_reviewed_at: datetime | None
    recommended_at: datetime

    model_config = {"from_attributes": True}

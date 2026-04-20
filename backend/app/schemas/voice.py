"""Schemas for voice-based memorization checking."""

from pydantic import BaseModel, Field


class TextCheckRequest(BaseModel):
    """Request body for text-based poem recitation check."""

    text: str
    hints_used: int = Field(default=0, ge=0)


class TranscribeResponse(BaseModel):
    """Response from transcribe-only endpoint."""

    text: str


class VoiceCheckResponse(BaseModel):
    """Response from voice-based poem recitation check."""

    transcribed_text: str
    accuracy_percent: float
    sm2_score: int  # 0-5, mapped from accuracy
    missed_lines: list[str]
    feedback: str
    next_steps: str  # "repeat" | "read_again" | "next_stanza" | "memorized"
    word_details: list[dict] = Field(default_factory=list)
    status: str  # SM-2 memorization status after update
    interval_days: int
    new_badges: list[dict] = Field(default_factory=list)
    challenge_progress: dict | None = None
    streak_freeze_used: bool = False

    model_config = {"from_attributes": True}

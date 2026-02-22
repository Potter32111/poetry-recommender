"""Schemas for voice-based memorization checking."""

from pydantic import BaseModel


class VoiceCheckResponse(BaseModel):
    """Response from voice-based poem recitation check."""

    transcribed_text: str
    accuracy_percent: float
    sm2_score: int  # 0-5, mapped from accuracy
    missed_lines: list[str]
    feedback: str
    next_steps: str  # "repeat" | "read_again" | "next_stanza" | "memorized"
    status: str  # SM-2 memorization status after update
    interval_days: int

    model_config = {"from_attributes": True}

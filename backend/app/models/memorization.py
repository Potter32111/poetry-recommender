import uuid
from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base


class Memorization(Base):
    """Tracks a user's progress memorizing a specific poem using SM-2 algorithm."""

    __tablename__ = "memorizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    poem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("poems.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="new"
    )  # new, learning, reviewing, memorized
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    score_history: Mapped[list] = mapped_column(JSONB, default=list)
    recommended_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="memorizations")
    poem = relationship("Poem", back_populates="memorizations")

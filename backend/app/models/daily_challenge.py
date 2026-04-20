"""Daily challenge model."""

import uuid
from datetime import datetime, date

from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DailyChallenge(Base):
    """A daily mini-goal assigned to each user."""

    __tablename__ = "daily_challenges"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_daily_challenges_user_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    goal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    goal_target: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    current_progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="daily_challenges")

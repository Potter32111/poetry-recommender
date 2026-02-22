import uuid
from datetime import datetime

from sqlalchemy import String, BigInteger, DateTime, Date, Integer, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """Telegram user with poetry preferences."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language_pref: Mapped[str] = mapped_column(String(10), default="both")  # "en", "ru", "both"
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_mood: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # --- Gamification and UI fields ---
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    ui_language: Mapped[str] = mapped_column(String(10), default="ru")
    notification_time: Mapped[str] = mapped_column(String(5), default="10:00")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    memorizations = relationship("Memorization", back_populates="user", lazy="selectin")

import uuid

from sqlalchemy import String, Text, SmallInteger, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.user import Base


class Poem(Base):
    """A poem stored in the system."""

    __tablename__ = "poems"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(5), nullable=False, index=True)  # "en" or "ru"
    difficulty: Mapped[int] = mapped_column(SmallInteger, default=3)  # 1-5
    themes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    era: Mapped[str | None] = mapped_column(String(50), nullable=True)
    lines_count: Mapped[int] = mapped_column(Integer, default=0)

    memorizations = relationship("Memorization", back_populates="poem", lazy="selectin")

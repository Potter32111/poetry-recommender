import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base

# SAFE MODE: Comment out vector import until installed
try:
    from pgvector.sqlalchemy import Vector
    HAS_VECTOR = True
except ImportError:
    HAS_VECTOR = False

class Poem(Base):
    __tablename__ = "poems"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, default=0.0)
    lines_count: Mapped[int] = mapped_column(Integer, nullable=False)
    themes: Mapped[list] = mapped_column(JSONB, default=list)
    era: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Vector embeddings for similarity search
    if HAS_VECTOR:
        embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
    else:
        embedding: Mapped[str | None] = mapped_column(Text, nullable=True)

    memorizations: Mapped[list["Memorization"]] = relationship("Memorization", back_populates="poem", lazy="selectin")

"""Collection and CollectionPoem models for curated themed playlists."""

import uuid

from sqlalchemy import String, Text, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Collection(Base):
    """A curated collection (playlist) of poems."""

    __tablename__ = "collections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    description_ru: Mapped[str] = mapped_column(Text, nullable=False, default="")
    description_en: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cover_emoji: Mapped[str] = mapped_column(String(10), nullable=False, default="📚")
    is_official: Mapped[bool] = mapped_column(Boolean, default=True)

    poems: Mapped[list["CollectionPoem"]] = relationship(
        "CollectionPoem", back_populates="collection", lazy="selectin",
        order_by="CollectionPoem.position",
    )


class CollectionPoem(Base):
    """Join table between collections and poems with ordering."""

    __tablename__ = "collection_poems"
    __table_args__ = (
        UniqueConstraint("collection_id", "poem_id", name="uq_collection_poem"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False
    )
    poem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("poems.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, default=0)

    collection = relationship("Collection", back_populates="poems")
    poem = relationship("Poem", lazy="selectin")

"""SQLAlchemy model for dictionary senses."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DictionarySense(Base):
    """Represents one meaning of a dictionary entry."""

    __tablename__ = "dictionary_senses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    entry_id: Mapped[int] = mapped_column(
        ForeignKey(
            "dictionary_entries.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    part_of_speech: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    definitions: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    examples: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    entry: Mapped["DictionaryEntry"] = relationship(
        back_populates="senses",
    )

    def __repr__(self) -> str:
        return (
            f"DictionarySense("
            f"id={self.id}, "
            f"part_of_speech='{self.part_of_speech}')"
        )
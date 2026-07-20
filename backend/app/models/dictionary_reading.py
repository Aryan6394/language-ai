"""SQLAlchemy model for dictionary readings."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DictionaryReading(Base):
    """Represents a pronunciation or reading of a dictionary entry."""

    __tablename__ = "dictionary_readings"

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

    script: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    reading: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    entry: Mapped["DictionaryEntry"] = relationship(
        back_populates="readings",
    )

    def __repr__(self) -> str:
        return (
            f"DictionaryReading("
            f"id={self.id}, "
            f"script='{self.script}', "
            f"reading='{self.reading}')"
        )
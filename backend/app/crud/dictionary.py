"""CRUD operations for dictionary entries."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    DictionaryEntry,
    DictionaryReading,
    DictionarySense,
)
from app.schemas.dictionary import DictionaryEntryData

__all__ = [
    "get_entry",
    "create_entry",
    "update_entry",
    "delete_entry",
    "search_entries",
]


async def get_entry(
    session: AsyncSession,
    *,
    word: str,
    language: str,
) -> DictionaryEntry | None:
    """
    Retrieve a dictionary entry by word and language.
    """

    stmt = (
        select(DictionaryEntry)
        .where(
            DictionaryEntry.word == word,
            DictionaryEntry.language == language,
        )
        .options(
            selectinload(DictionaryEntry.readings),
            selectinload(DictionaryEntry.senses),
        )
    )

    result = await session.execute(stmt)

    return result.scalar_one_or_none()


async def create_entry(
    session: AsyncSession,
    entry: DictionaryEntryData,
) -> DictionaryEntry:
    """
    Create a new dictionary entry.
    """

    db_entry = DictionaryEntry(
        word=entry.word,
        language=entry.language,
    )

    db_entry.readings.extend(
        DictionaryReading(
            script=reading.script,
            reading=reading.reading,
        )
        for reading in entry.readings
    )

    db_entry.senses.extend(
        DictionarySense(
            part_of_speech=sense.part_of_speech,
            definitions=sense.definitions,
            examples=sense.examples,
        )
        for sense in entry.senses
    )

    session.add(db_entry)

    await session.commit()

    stmt = (
    select(DictionaryEntry)
    .where(DictionaryEntry.id == db_entry.id)
    .options(
        selectinload(DictionaryEntry.readings),
        selectinload(DictionaryEntry.senses),
    )
)

    result = await session.execute(stmt)

    return result.scalar_one()


async def update_entry(
    session: AsyncSession,
    db_entry: DictionaryEntry,
    entry: DictionaryEntryData,
) -> DictionaryEntry:
    """
    Replace an existing dictionary entry.
    """

    db_entry.word = entry.word
    db_entry.language = entry.language

    db_entry.readings.clear()
    db_entry.senses.clear()

    db_entry.readings.extend(
        DictionaryReading(
            script=reading.script,
            reading=reading.reading,
        )
        for reading in entry.readings
    )

    db_entry.senses.extend(
        DictionarySense(
            part_of_speech=sense.part_of_speech,
            definitions=sense.definitions,
            examples=sense.examples,
        )
        for sense in entry.senses
    )

    await session.commit()
    stmt = (
        select(DictionaryEntry)
        .where(DictionaryEntry.id == db_entry.id)
        .options(
            selectinload(DictionaryEntry.readings),
            selectinload(DictionaryEntry.senses),
        )
    )

    result = await session.execute(stmt)

    return result.scalar_one()

async def delete_entry(
    session: AsyncSession,
    db_entry: DictionaryEntry,
) -> None:
    """
    Delete a dictionary entry.
    """

    await session.delete(db_entry)

    await session.commit()


async def search_entries(
    session: AsyncSession,
    *,
    language: str,
    query: str,
    limit: int = 20,
) -> list[DictionaryEntry]:
    """
    Search dictionary entries by word.
    """

    stmt = (
        select(DictionaryEntry)
        .where(
            DictionaryEntry.language == language,
            DictionaryEntry.word.ilike(f"%{query}%"),
        )
        .order_by(DictionaryEntry.word)
        .limit(limit)
        .options(
            selectinload(DictionaryEntry.readings),
            selectinload(DictionaryEntry.senses),
        )
    )

    result = await session.execute(stmt)

    return list(result.scalars().all())
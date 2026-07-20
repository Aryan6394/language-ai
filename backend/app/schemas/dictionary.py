"""Pydantic schemas for dictionary requests and responses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DictionaryLookupRequest(BaseModel):
    """Request to look up a word in a language."""

    word: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Word or phrase to look up.",
    )

    language: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Target language code (e.g. 'ja', 'en', 'de').",
    )


class DictionaryReading(BaseModel):
    """Pronunciation or reading of a dictionary entry."""

    script: str = Field(
        ...,
        description="Writing system (e.g. kanji, hiragana, romaji).",
    )

    reading: str = Field(
        ...,
        description="Pronunciation or reading.",
    )


class DictionarySense(BaseModel):
    """Single meaning of a dictionary entry."""

    part_of_speech: str = Field(
        ...,
        description="Part of speech (noun, verb, adjective, etc.).",
    )

    definitions: list[str] = Field(
        default_factory=list,
        description="Definitions for this sense.",
    )

    examples: list[str] = Field(
        default_factory=list,
        description="Example sentences.",
    )


class DictionaryEntryData(BaseModel):
    """Validated dictionary entry used internally by the application."""

    word: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    language: str = Field(
        ...,
        min_length=2,
        max_length=20,
    )

    readings: list[DictionaryReading] = Field(
        default_factory=list,
    )

    senses: list[DictionarySense] = Field(
        default_factory=list,
    )


class DictionaryResponse(BaseModel):
    """Dictionary entry returned by the api."""

    model_config = ConfigDict(from_attributes=True)

    word: str

    language: str

    readings: list[DictionaryReading] = Field(
        default_factory=list,
    )

    senses: list[DictionarySense] = Field(
        default_factory=list,
    )


__all__ = [
    "DictionaryLookupRequest",
    "DictionaryReading",
    "DictionarySense",
    "DictionaryEntryData",
    "DictionaryResponse",
]
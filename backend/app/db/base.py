"""
Declarative base for all SQLAlchemy models.

Every model imports `Base` from here so they share the same metadata.
Alembic uses this metadata to discover and generate database migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass
"""Database session configuration."""
"""
Database engine and session management.

Connection details come from app.core.config.Settings (`database_url`),
which reads DATABASE_URL from the environment (see backend/.env.example).

This module provides both synchronous and asynchronous SQLAlchemy
sessions.

Sync sessions are used by the existing authentication, users,
languages, and vocabulary modules.

Async sessions are used by AI-powered modules such as Dictionary,
where asynchronous HTTP calls to AI providers fit naturally into the
request flow.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

# --------------------------------------------------------------------------
# Synchronous engine
# --------------------------------------------------------------------------

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# --------------------------------------------------------------------------
# Asynchronous engine
# --------------------------------------------------------------------------

async_database_url = settings.database_url.replace(
    "postgresql://",
    "postgresql+asyncpg://",
    1,
)

async_engine = create_async_engine(
    async_database_url,
    pool_pre_ping=True,
    
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
)

# --------------------------------------------------------------------------
# Sync dependency
# --------------------------------------------------------------------------

def get_db() -> Session:
    """
    FastAPI dependency that yields a request-scoped synchronous
    database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------------------------------
# Async dependency
# --------------------------------------------------------------------------

async def get_async_db() -> AsyncSession:
    """
    FastAPI dependency that yields a request-scoped asynchronous
    database session.
    """
    async with AsyncSessionLocal() as session:
        yield session


__all__ = [
    "engine",
    "async_engine",
    "SessionLocal",
    "AsyncSessionLocal",
    "get_db",
    "get_async_db",
]
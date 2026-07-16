"""Database session configuration."""
"""
Database engine and session management.

Connection details come from app.core.config.Settings (`database_url`),
which reads DATABASE_URL from the environment (see backend/.env.example).
Primary store is PostgreSQL, per DATABASE.md.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# pool_pre_ping tests each pooled connection before handing it to a
# request, so a stale/dropped connection (e.g. free-tier DB restart)
# is replaced quietly instead of surfacing as a mid-request error.
engine = create_engine(settings.database_url, pool_pre_ping=True)

# autocommit=False: nothing is written until code calls db.commit()
# explicitly (matches every CRUD function in the project).
# autoflush=False: pending changes aren't silently flushed ahead of a
# query, keeping write timing explicit.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    FastAPI dependency that yields a request-scoped DB session
    and guarantees it is closed afterward, even if the request raised.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
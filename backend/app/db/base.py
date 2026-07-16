"""
Declarative base for all SQLAlchemy models.

Every model file (e.g. app/models/user.py, app/models/vocabulary.py)
imports `Base` from here and registers itself against the same MetaData
object, so that Base.metadata.create_all(engine) / Alembic autogenerate
can see all tables across every domain in DATABASE.md.

No model classes are defined in this file — it only provides the base
class to inherit from.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
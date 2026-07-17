"""User-related models."""
"""
SQLAlchemy model for the `users` table (DATABASE.md, Section 1.1).

Milestone 2 (Authentication) scope note: this file implements only the
`User` ORM model itself. Deliberately NOT included here, per current task
requirements:
  - Pydantic schemas (request/response shapes)
  - CRUD functions
  - Routers/endpoints
  - Password hashing (no hashing library wired in — `password_hash` is
    just a plain string column; hashing logic belongs to a future
    app/core/security.py)
  - JWT issuance/validation

`user_settings` (DATABASE.md Section 1.2) is a separate table/model and is
intentionally not implemented here either — this pass covers `users` only.
"""

import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from sqlalchemy.orm import relationship

class AccountStatus(str, enum.Enum):
    """Mirrors DATABASE.md's `account_status` enum (active, deleted, suspended)."""

    active = "active"
    deleted = "deleted"
    suspended = "suspended"


class User(Base):
    __tablename__ = "users"

    # Primary key. Generated client-side (Python `uuid4`) rather than
    # relying on a DB-side default, matching the convention already used
    # in app/models/vocabulary.py.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # The user's email address, used for login and account recovery.
    # Nullable because guest accounts (see `is_guest` below) don't have
    # one until the account is claimed. Enforced unique at the DB level
    # so two accounts can't share an email.
    email = Column(String, unique=True, nullable=True, index=True)

    # Hashed password, not the plaintext password. Nullable because
    # guest accounts and any future social-login-only accounts won't
    # have a password at all. NOTE: no hashing is implemented in this
    # pass — this column simply reserves the space for a hash string
    # produced elsewhere (future app/core/security.py).
    password_hash = Column(String, nullable=True)

    # The name shown in the app (profile, leaderboard, etc.). Distinct
    # from email so it can be changed freely without touching login
    # credentials.
    display_name = Column(String, nullable=False)

    # Foreign key to the user's base/native language (DATABASE.md
    # Section 2.1, `languages` table). Plain FK column only — no
    # `relationship()` is declared here since the `Language` model
    # doesn't exist yet in this pass, and DATABASE.md's "add
    # relationships only if required" guidance means this isn't needed
    # until something actually needs to join across it.
    native_language_id = Column(UUID(as_uuid=True), ForeignKey("languages.id"), nullable=True)

    # True until the guest account is "claimed" by adding a real email
    # + password via signup. Lets the app support try-before-signup
    # flows (see TASKS.md, guest mode).
    is_guest = Column(Boolean, nullable=False, default=False)

    # Current lifecycle state of the account. `deleted`/`suspended`
    # support the account-deletion and moderation flows described in
    # TASKS.md, without physically removing the row.
    account_status = Column(
        Enum(AccountStatus, name="account_status"),
        nullable=False,
        default=AccountStatus.active,
    )

    # When the account was created. Server-generated so it's always
    # accurate regardless of what the client sends.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

        # Last time the user did anything active in the app. DATABASE.md
    # notes this "drives streak calculation" — see the open design
    # question in the project audit about whether streaks are global
    # or per-language; this column exists either way as the raw
    # last-activity signal.
    last_active_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    languages = relationship(
        "UserLanguage",
        back_populates="user",
    )
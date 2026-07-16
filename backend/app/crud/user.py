"""
CRUD functions for the `User` model (DATABASE.md Section 1.1).

Scope note: this file implements only the four functions below. No
routers, no JWT, no login flow, no auth dependencies — those consume
these functions later but aren't defined here.
"""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user from a UserCreate schema.

    The plaintext password from the schema is hashed via
    hash_password() before it ever touches the User model — the
    plaintext value itself is never stored or passed to the DB layer.
    """
    db_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        display_name=user.display_name,
        native_language_id=user.native_language_id,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Look up a user by email. Returns None if no match exists."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """Look up a user by primary key. Returns None if no match exists."""
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    """
    Apply a partial update to an existing User.

    Only fields the client actually included in the request are
    touched: `model_dump(exclude_unset=True)` returns just the fields
    that were explicitly set on `user_update`, so an omitted field is
    left completely alone rather than being overwritten with its
    schema default (None). If a field IS explicitly sent as null,
    that's treated as an intentional clear and is applied.
    """
    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
    
"""
CRUD functions for the `User` model (DATABASE.md Section 1.1).

Scope note: this file implements the functions below. No routers, no
JWT issuance itself, no login route — those consume `authenticate_user`
but aren't defined here.
"""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user from a UserCreate schema.

    The plaintext password from the schema is hashed before it is ever
    stored. Only the resulting password hash is persisted to the
    database.
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
    """
    Retrieve a user by email.

    Returns:
        User if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """
    Retrieve a user by primary key.

    Uses SQLAlchemy's Session.get(), which is the preferred and most
    efficient way to load a row by its primary key.
    """
    return db.get(User, user_id)


def update_user(
    db: Session,
    db_user: User,
    user_update: UserUpdate,
) -> User:
    """
    Partially update an existing user.

    Only fields explicitly supplied by the client are modified.
    """

    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> Optional[User]:
    """
    Authenticate a user using email and password.

    Returns:
        User on successful authentication.

        None if:
        - the email does not exist
        - the account has no password hash
        - the password is incorrect

    Returning the same result for every failure case avoids leaking
    whether a particular email address is registered.
    """

    db_user = get_user_by_email(db, email)

    if db_user is None:
        return None

    if db_user.password_hash is None:
        return None

    if not verify_password(password, db_user.password_hash):
        return None

    return db_user
def change_password(
    db: Session,
    db_user: User,
    current_password: str,
    new_password: str,
) -> bool:
    """
    Change the authenticated user's password.

    Returns:
        True if the password was successfully changed.

        False if the current password is incorrect.
    """

    if not verify_password(current_password, db_user.password_hash):
        return False

    db_user.password_hash = hash_password(new_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return True
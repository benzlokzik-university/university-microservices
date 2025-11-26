"""
Authentication utilities for User Account service.
"""

import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # Ensure password is bytes for bcrypt
    if isinstance(plain_password, str):
        plain_password = plain_password.encode("utf-8")

    # Truncate to 72 bytes if necessary
    if len(plain_password) > 72:
        plain_password = plain_password[:72]

    # Ensure hashed_password is bytes
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode("utf-8")

    return bcrypt.checkpw(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    # Ensure password is bytes for bcrypt
    if isinstance(password, str):
        password = password.encode("utf-8")

    # Truncate to 72 bytes to avoid bcrypt limitation
    # bcrypt has a hard limit of 72 bytes for passwords
    if len(password) > 72:
        password = password[:72]

    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)

    # Return as string (bcrypt returns bytes)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

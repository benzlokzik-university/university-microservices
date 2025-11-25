"""
Database models for User Account service.
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base
import uuid


def generate_id():
    """Generate a unique ID."""
    return str(uuid.uuid4())


class User(Base):
    """User model for the database."""
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=generate_id)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    is_blocked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


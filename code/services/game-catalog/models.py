"""
Database models for Game Catalog service.
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from database import Base
import uuid
import json


def generate_id():
    """Generate a unique ID."""
    return str(uuid.uuid4())


class StringArray(TypeDecorator):
    """A type that works with both PostgreSQL ARRAY and SQLite (using JSON in Text)."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String))
        else:
            # For SQLite and other databases, use Text to store JSON
            return dialect.type_descriptor(Text)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        else:
            # For SQLite, convert list to JSON string
            if isinstance(value, list):
                return json.dumps(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        if dialect.name == "postgresql":
            return value if value is not None else []
        else:
            # For SQLite, parse JSON string to list
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return []
            return value if value is not None else []


class Game(Base):
    """Game model for the database."""

    __tablename__ = "games"

    game_id = Column(String, primary_key=True, default=generate_id)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    min_players = Column(Integer, nullable=False)
    max_players = Column(Integer, nullable=False)
    play_time_minutes = Column(Integer, nullable=True)
    age_rating = Column(Integer, nullable=True)
    category = Column(String, nullable=True, index=True)
    price_per_day = Column(Float, nullable=False)
    total_copies = Column(Integer, nullable=False, default=1)
    available_count = Column(Integer, nullable=False, default=1)
    status = Column(
        String, default="available", nullable=False
    )  # available, unavailable, reserved, rented, inspection, repair
    photo_urls = Column(StringArray, default=[], nullable=False)
    rating = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

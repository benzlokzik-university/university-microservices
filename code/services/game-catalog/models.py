"""
Database models for Game Catalog service.
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from database import Base
import uuid


def generate_id():
    """Generate a unique ID."""
    return str(uuid.uuid4())


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
    status = Column(String, default="available", nullable=False)  # available, unavailable, reserved, rented, inspection, repair
    photo_urls = Column(ARRAY(String), default=[], nullable=False)
    rating = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


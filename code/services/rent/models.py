"""
Database models for Rent service.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.sql import func
from database import Base
import uuid


def generate_id():
    """Generate a unique ID."""
    return str(uuid.uuid4())


class Order(Base):
    """Order model for the database."""

    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, default=generate_id)
    booking_id = Column(String, nullable=False)
    game_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    status = Column(
        String, default="created", nullable=False
    )  # created, confirmed, active, completed, returned
    pickup_date = Column(DateTime(timezone=True), nullable=False)
    pickup_location = Column(String, nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    rental_days = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
    penalty_amount = Column(Float, default=0.0, nullable=False)
    payment_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

"""
Pydantic schemas for Booking service.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BookGameRequest(BaseModel):
    """Request schema for booking a game."""

    game_id: str
    user_id: str
    booking_date: datetime
    pickup_date: datetime


class CancelBookingRequest(BaseModel):
    """Request schema for canceling a booking."""

    user_id: str
    reason: Optional[str] = Field(None, max_length=500)


class BookingResponse(BaseModel):
    """Response schema for booking information."""

    booking_id: str
    game_id: str
    user_id: str
    status: str  # pending, confirmed, canceled
    booking_date: datetime
    pickup_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}

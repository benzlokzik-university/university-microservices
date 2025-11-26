"""
Pydantic schemas for Rent service.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BookingResponse(BaseModel):
    """Response schema for booking information from Booking service."""

    booking_id: str
    game_id: str
    user_id: str
    status: str
    pickup_date: datetime

    model_config = {"from_attributes": True}


class CreateOrderRequest(BaseModel):
    """Request schema for creating an order."""

    booking_id: str
    user_id: str
    pickup_location: str = Field(..., max_length=200)
    rental_days: int = Field(..., ge=1, le=30)


class SendPickupNotificationRequest(BaseModel):
    """Request schema for sending pickup notification."""

    pickup_date: datetime
    pickup_location: str = Field(..., max_length=200)


class ConfirmGameReceiptRequest(BaseModel):
    """Request schema for confirming game receipt."""

    user_id: str


class SendReturnReminderRequest(BaseModel):
    """Request schema for sending return reminder."""

    return_date: datetime


class ExtendRentalPeriodRequest(BaseModel):
    """Request schema for extending rental period."""

    user_id: str
    additional_days: int = Field(..., ge=1, le=7)


class EndRentalPeriodRequest(BaseModel):
    """Request schema for ending rental period."""

    pass


class ReturnGameRequest(BaseModel):
    """Request schema for returning game."""

    user_id: str
    return_location: str = Field(..., max_length=200)


class ChargePenaltyRequest(BaseModel):
    """Request schema for charging penalty."""

    penalty_amount: float = Field(..., ge=0)
    reason: str = Field(..., max_length=500)


class ConfirmGameReturnRequest(BaseModel):
    """Request schema for confirming game return."""

    game_condition: str = Field(..., max_length=200)


class OrderResponse(BaseModel):
    """Response schema for order information."""

    order_id: str
    booking_id: str
    game_id: str
    user_id: str
    status: str
    pickup_date: datetime
    pickup_location: str
    return_date: Optional[datetime]
    rental_days: int
    total_amount: float
    penalty_amount: Optional[float]
    payment_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

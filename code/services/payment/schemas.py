"""
Pydantic schemas for Payment service.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class InitiatePaymentRequest(BaseModel):
    """Request schema for initiating payment."""
    order_id: str
    user_id: str
    amount: float = Field(..., ge=0)
    payment_method: str = Field(..., max_length=50)


class ProcessPaymentRequest(BaseModel):
    """Request schema for processing payment."""
    payment_id: str
    transaction_id: str


class RequestRefundRequest(BaseModel):
    """Request schema for requesting refund."""
    payment_id: str
    user_id: str
    reason: str = Field(..., max_length=500)
    amount: Optional[float] = Field(None, ge=0)


class ProcessRefundRequest(BaseModel):
    """Request schema for processing refund."""
    refund_id: str
    transaction_id: str


class DeclineRefundRequest(BaseModel):
    """Request schema for declining refund."""
    refund_id: str
    reason: str = Field(..., max_length=500)


class PaymentResponse(BaseModel):
    """Response schema for payment information."""
    payment_id: str
    order_id: str
    user_id: str
    amount: float
    status: str  # initiated, processing, completed, declined, refunded
    payment_method: str
    transaction_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class RefundResponse(BaseModel):
    """Response schema for refund information."""
    refund_id: str
    payment_id: str
    user_id: str
    amount: float
    status: str  # requested, processing, completed, declined
    reason: str
    transaction_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


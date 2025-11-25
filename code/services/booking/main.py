"""
Booking Service - FastAPI application.

This service handles game bookings. It calls the User Account service
to validate users (nested function call requirement).
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn
import uuid

from schemas import BookGameRequest, CancelBookingRequest, BookingResponse
from user_service import validate_user, get_user
from rabbitmq_client import publish_event


# In-memory storage for bookings (in production, use a database)
bookings_db = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    print("🚀 Booking service starting up...")
    yield
    print("🛑 Booking service shutting down...")


app = FastAPI(
    title="Booking Service",
    description="Service for managing game bookings",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/api/v1/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Bookings"],
    summary="Book a game",
)
async def book_game(request: BookGameRequest):
    """
    Book a game for a user.

    This endpoint calls the User Account service to validate that the user
    exists and is not blocked (nested function call).
    """
    # Validate user by calling User Account service (nested function call)
    is_valid = await validate_user(request.user_id)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found or blocked"
        )

    # Create booking
    booking_id = str(uuid.uuid4())
    booking = {
        "booking_id": booking_id,
        "game_id": request.game_id,
        "user_id": request.user_id,
        "status": "pending",
        "booking_date": request.booking_date,
        "pickup_date": request.pickup_date,
        "created_at": datetime.now(),
    }

    bookings_db[booking_id] = booking

    # Publish domain event
    await publish_event(
        "booking.created",
        {
            "booking_id": booking_id,
            "game_id": request.game_id,
            "user_id": request.user_id,
            "status": "pending",
        },
    )

    return BookingResponse(**booking)


@app.post(
    "/api/v1/bookings/{booking_id}/cancel",
    response_model=BookingResponse,
    tags=["Bookings"],
    summary="Cancel a booking",
)
async def cancel_booking(booking_id: str, request: CancelBookingRequest):
    """Cancel a booking."""
    booking = bookings_db.get(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    # Verify user owns the booking
    if booking["user_id"] != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this booking",
        )

    # Update booking status
    booking["status"] = "canceled"
    bookings_db[booking_id] = booking

    # Publish domain event
    await publish_event(
        "booking.canceled",
        {
            "booking_id": booking_id,
            "user_id": request.user_id,
            "reason": request.reason,
        },
    )

    return BookingResponse(**booking)


@app.get(
    "/api/v1/bookings/{booking_id}",
    response_model=BookingResponse,
    tags=["Bookings"],
    summary="Get booking information",
)
async def get_booking(booking_id: str):
    """Get booking information by ID."""
    booking = bookings_db.get(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    return BookingResponse(**booking)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "booking"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)

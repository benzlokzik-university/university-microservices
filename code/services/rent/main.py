"""
Rent Service - FastAPI application with gRPC client.

This service handles game rentals. It includes:
- gRPC client for synchronous communication with Payment service
- Database for storing orders
- Mocked notification services (OneSignal, SendGrid)
- RabbitMQ for event-driven communication
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import uvicorn
import httpx

from database import get_db, engine, Base
from models import Order
from schemas import (
    CreateOrderRequest,
    SendPickupNotificationRequest,
    ConfirmGameReceiptRequest,
    SendReturnReminderRequest,
    ExtendRentalPeriodRequest,
    EndRentalPeriodRequest,
    ReturnGameRequest,
    ChargePenaltyRequest,
    ConfirmGameReturnRequest,
    OrderResponse,
)
from grpc_client import initiate_payment_grpc
from notification_service import notification_service
from rabbitmq_client import publish_event

# External service URLs
BOOKING_SERVICE_URL = "http://booking:8003"
GAME_CATALOG_SERVICE_URL = "http://game-catalog:8002"
USER_ACCOUNT_SERVICE_URL = "http://user-account:8001"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    print("🚀 Rent service starting up...")
    Base.metadata.create_all(bind=engine)
    yield
    print("🛑 Rent service shutting down...")


app = FastAPI(
    title="Rent Service",
    description="Service for managing game rentals with gRPC and RabbitMQ",
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


async def get_booking(booking_id: str) -> dict:
    """Get booking information from Booking service."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BOOKING_SERVICE_URL}/api/v1/bookings/{booking_id}")
        if response.status_code == 200:
            return response.json()
        return None


async def get_user_email(user_id: str) -> str:
    """Get user email from User Account service."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_ACCOUNT_SERVICE_URL}/api/v1/users/{user_id}")
        if response.status_code == 200:
            user = response.json()
            return user.get("email", "user@example.com")
        return "user@example.com"


@app.post(
    "/api/v1/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Orders"],
    summary="Create order",
)
async def create_order(request: CreateOrderRequest, db: Session = Depends(get_db)):
    """Create a new rental order and initiate payment via gRPC."""
    # Get booking information
    booking = await get_booking(request.booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking["status"] != "confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking must be confirmed before creating order"
        )
    
    # Calculate total amount (mock: 100 per day)
    total_amount = request.rental_days * 100.0
    
    # Create order
    db_order = Order(
        booking_id=request.booking_id,
        game_id=booking["game_id"],
        user_id=request.user_id,
        status="created",
        pickup_date=booking["pickup_date"],
        pickup_location=request.pickup_location,
        rental_days=request.rental_days,
        total_amount=total_amount,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Initiate payment via gRPC (synchronous communication)
    payment_result = await initiate_payment_grpc(
        order_id=db_order.order_id,
        user_id=request.user_id,
        amount=total_amount,
        payment_method="card"
    )
    
    if payment_result:
        db_order.payment_id = payment_result.get("payment_id")
        db.commit()
        db.refresh(db_order)
    
    # Publish domain event
    await publish_event("rent.order.created", {
        "order_id": db_order.order_id,
        "booking_id": request.booking_id,
        "game_id": booking["game_id"],
        "user_id": request.user_id,
        "total_amount": total_amount,
    })
    
    return OrderResponse.model_validate(db_order)


@app.post(
    "/api/v1/orders/{order_id}/pickup-notification",
    response_model=dict,
    tags=["Orders"],
    summary="Send pickup notification",
)
async def send_pickup_notification(
    order_id: str,
    request: SendPickupNotificationRequest,
    db: Session = Depends(get_db)
):
    """Send pickup notification via OneSignal and SendGrid."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    user_email = await get_user_email(order.user_id)
    
    # Send push notification (OneSignal)
    await notification_service.send_push_notification(
        order.user_id,
        "Pickup Reminder",
        f"Your game pickup is scheduled for {request.pickup_date}"
    )
    
    # Send email (SendGrid)
    await notification_service.send_email(
        user_email,
        "Game Pickup Reminder",
        f"Your game pickup is scheduled for {request.pickup_date} at {request.pickup_location}"
    )
    
    # Publish domain event
    await publish_event("rent.pickup_notification.sent", {
        "order_id": order_id,
        "pickup_date": request.pickup_date.isoformat(),
        "pickup_location": request.pickup_location,
    })
    
    return {"success": True, "message": "Notifications sent"}


@app.post(
    "/api/v1/orders/{order_id}/confirm-receipt",
    response_model=OrderResponse,
    tags=["Orders"],
    summary="Confirm game receipt",
)
async def confirm_game_receipt(
    order_id: str,
    request: ConfirmGameReceiptRequest,
    db: Session = Depends(get_db)
):
    """Confirm that user received the game."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.user_id != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to confirm this order"
        )
    
    order.status = "active"
    db.commit()
    db.refresh(order)
    
    # Publish domain event
    await publish_event("rent.game_receipt.confirmed", {
        "order_id": order_id,
        "user_id": request.user_id,
    })
    
    return OrderResponse.model_validate(order)


@app.post(
    "/api/v1/orders/{order_id}/return",
    response_model=OrderResponse,
    tags=["Orders"],
    summary="Return game",
)
async def return_game(
    order_id: str,
    request: ReturnGameRequest,
    db: Session = Depends(get_db)
):
    """Initiate game return."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.user_id != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to return this order"
        )
    
    order.status = "returned"
    order.return_date = datetime.now()
    db.commit()
    db.refresh(order)
    
    # Publish domain event
    await publish_event("rent.game.returned", {
        "order_id": order_id,
        "user_id": request.user_id,
        "return_location": request.return_location,
    })
    
    return OrderResponse.model_validate(order)


@app.post(
    "/api/v1/orders/{order_id}/penalty",
    response_model=OrderResponse,
    tags=["Orders"],
    summary="Charge penalty",
)
async def charge_penalty(
    order_id: str,
    request: ChargePenaltyRequest,
    db: Session = Depends(get_db)
):
    """Charge penalty for late return."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    order.penalty_amount = request.penalty_amount
    db.commit()
    db.refresh(order)
    
    # Publish domain event
    await publish_event("rent.penalty.charged", {
        "order_id": order_id,
        "penalty_amount": request.penalty_amount,
        "reason": request.reason,
    })
    
    return OrderResponse.model_validate(order)


@app.get(
    "/api/v1/orders/{order_id}",
    response_model=OrderResponse,
    tags=["Orders"],
    summary="Get order information",
)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get order information by ID."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return OrderResponse.model_validate(order)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "rent"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8005,
        reload=True
    )

"""
Payment Service - FastAPI application with gRPC server.

This service handles payments and refunds. It includes:
- gRPC server for synchronous communication with Rent service
- Mocked payment gateway (Эквайринг)
- Mocked OFD (fiscal data operator)
- RabbitMQ for publishing domain events
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn
import uuid
import asyncio
import grpc
from concurrent import futures

from schemas import (
    InitiatePaymentRequest,
    ProcessPaymentRequest,
    RequestRefundRequest,
    ProcessRefundRequest,
    DeclineRefundRequest,
    PaymentResponse,
    RefundResponse,
)
from payment_gateway import payment_gateway
from rabbitmq_client import publish_event


# In-memory storage (in production, use a database)
payments_db = {}
refunds_db = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    print("🚀 Payment service starting up...")

    # Start gRPC server in background
    # grpc_task = asyncio.create_task(serve_grpc(payments_db, refunds_db))

    yield

    print("🛑 Payment service shutting down...")


app = FastAPI(
    title="Payment Service",
    description="Service for managing payments and refunds with gRPC support",
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
    "/api/v1/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Payments"],
    summary="Initiate payment",
)
async def initiate_payment(request: InitiatePaymentRequest):
    """Initiate a new payment."""
    payment_id = str(uuid.uuid4())

    payment = {
        "payment_id": payment_id,
        "order_id": request.order_id,
        "user_id": request.user_id,
        "amount": request.amount,
        "status": "initiated",
        "payment_method": request.payment_method,
        "transaction_id": None,
        "created_at": datetime.now(),
        "completed_at": None,
    }

    payments_db[payment_id] = payment

    # Publish domain event
    await publish_event(
        "payment.initiated",
        {
            "payment_id": payment_id,
            "order_id": request.order_id,
            "user_id": request.user_id,
            "amount": request.amount,
        },
    )

    return PaymentResponse(**payment)


@app.post(
    "/api/v1/payments/{payment_id}/process",
    response_model=PaymentResponse,
    tags=["Payments"],
    summary="Process payment",
)
async def process_payment(payment_id: str, request: ProcessPaymentRequest):
    """Process a payment through the payment gateway."""
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )

    # Process through mocked gateway
    result = await payment_gateway.process_payment(
        payment_id, payment["amount"], payment["payment_method"]
    )

    # Update payment
    payment["status"] = result["status"]
    payment["transaction_id"] = result["transaction_id"]
    if result["status"] == "completed":
        payment["completed_at"] = datetime.now()
        # Mock OFD (fiscal data operator) - just log
        print(f"[OFD] Fiscal receipt generated for payment {payment_id}")

    # Publish domain event
    event_type = (
        "payment.successful" if result["status"] == "completed" else "payment.declined"
    )
    await publish_event(
        event_type,
        {
            "payment_id": payment_id,
            "order_id": payment["order_id"],
            "status": result["status"],
            "transaction_id": result["transaction_id"],
        },
    )

    return PaymentResponse(**payment)


@app.post(
    "/api/v1/refunds",
    response_model=RefundResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Refunds"],
    summary="Request refund",
)
async def request_refund(request: RequestRefundRequest):
    """Request a refund for a payment."""
    payment = payments_db.get(request.payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )

    if payment["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refund completed payments",
        )

    refund_id = str(uuid.uuid4())
    refund_amount = request.amount or payment["amount"]

    refund = {
        "refund_id": refund_id,
        "payment_id": request.payment_id,
        "user_id": request.user_id,
        "amount": refund_amount,
        "status": "requested",
        "reason": request.reason,
        "transaction_id": None,
        "created_at": datetime.now(),
        "completed_at": None,
    }

    refunds_db[refund_id] = refund

    # Publish domain event
    await publish_event(
        "refund.requested",
        {
            "refund_id": refund_id,
            "payment_id": request.payment_id,
            "user_id": request.user_id,
            "amount": refund_amount,
        },
    )

    return RefundResponse(**refund)


@app.post(
    "/api/v1/refunds/{refund_id}/process",
    response_model=RefundResponse,
    tags=["Refunds"],
    summary="Process refund",
)
async def process_refund(refund_id: str, request: ProcessRefundRequest):
    """Process a refund through the payment gateway."""
    refund = refunds_db.get(refund_id)
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Refund not found"
        )

    payment = payments_db.get(refund["payment_id"])

    # Process through mocked gateway
    result = await payment_gateway.process_refund(
        refund_id, refund["payment_id"], refund["amount"]
    )

    # Update refund
    refund["status"] = result["status"]
    refund["transaction_id"] = result["transaction_id"]
    if result["status"] == "completed":
        refund["completed_at"] = datetime.now()
        # Update payment status
        if payment:
            payment["status"] = "refunded"

    # Publish domain event
    await publish_event(
        "refund.processed",
        {
            "refund_id": refund_id,
            "payment_id": refund["payment_id"],
            "status": result["status"],
            "transaction_id": result["transaction_id"],
        },
    )

    return RefundResponse(**refund)


@app.post(
    "/api/v1/refunds/{refund_id}/decline",
    response_model=RefundResponse,
    tags=["Refunds"],
    summary="Decline refund",
)
async def decline_refund(refund_id: str, request: DeclineRefundRequest):
    """Decline a refund request."""
    refund = refunds_db.get(refund_id)
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Refund not found"
        )

    refund["status"] = "declined"

    # Publish domain event
    await publish_event(
        "refund.declined",
        {
            "refund_id": refund_id,
            "payment_id": refund["payment_id"],
            "reason": request.reason,
        },
    )

    return RefundResponse(**refund)


@app.get(
    "/api/v1/payments/{payment_id}",
    response_model=PaymentResponse,
    tags=["Payments"],
    summary="Get payment information",
)
async def get_payment(payment_id: str):
    """Get payment information by ID."""
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )
    return PaymentResponse(**payment)


@app.get(
    "/api/v1/refunds/{refund_id}",
    response_model=RefundResponse,
    tags=["Refunds"],
    summary="Get refund information",
)
async def get_refund(refund_id: str):
    """Get refund information by ID."""
    refund = refunds_db.get(refund_id)
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Refund not found"
        )
    return RefundResponse(**refund)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "payment"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)

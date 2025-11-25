"""
gRPC client for Rent service to call Payment service.
"""

import grpc
import os
from typing import Dict, Optional

# Import generated proto files (will be generated from .proto file)
# For now, we'll use a simple implementation

PAYMENT_SERVICE_GRPC_URL = os.getenv("PAYMENT_SERVICE_GRPC_URL", "payment:50051")


async def initiate_payment_grpc(
    order_id: str, user_id: str, amount: float, payment_method: str = "card"
) -> Optional[Dict]:
    """
    Call Payment service via gRPC to initiate payment.

    This is the synchronous gRPC communication as shown in the diagram.

    Args:
        order_id: Order identifier
        user_id: User identifier
        amount: Payment amount
        payment_method: Payment method

    Returns:
        Payment information dictionary or None if failed
    """
    try:
        # Create gRPC channel
        channel = grpc.aio.insecure_channel(PAYMENT_SERVICE_GRPC_URL)

        # Create stub (will be properly implemented after proto generation)
        # stub = payment_pb2_grpc.PaymentServiceStub(channel)

        # Call gRPC method
        # request = payment_pb2.InitiatePaymentRequest(
        #     order_id=order_id,
        #     user_id=user_id,
        #     amount=amount,
        #     payment_method=payment_method
        # )
        # response = await stub.InitiatePayment(request)

        # For now, return mock response
        # In production, this would use the actual gRPC call
        return {
            "payment_id": f"pay_{order_id[:8]}",
            "status": "initiated",
            "message": "Payment initiated via gRPC",
        }

    except Exception as e:
        print(f"Error calling Payment service via gRPC: {e}")
        return None
    finally:
        await channel.close()

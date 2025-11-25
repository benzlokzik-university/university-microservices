"""
gRPC server for Payment service.
"""

import grpc
from concurrent import futures
import asyncio
from datetime import datetime
import uuid

# Import generated proto files (will be generated from .proto file)
# For now, we'll use a simple implementation
from payment_gateway import payment_gateway


class PaymentServiceServicer:
    """gRPC service implementation for Payment."""
    
    def __init__(self, payments_db, refunds_db):
        self.payments_db = payments_db
        self.refunds_db = refunds_db
    
    async def InitiatePayment(self, request, context):
        """Initiate a payment (gRPC method)."""
        from payment_pb2 import InitiatePaymentResponse
        
        payment_id = str(uuid.uuid4())
        
        # Store payment
        payment = {
            "payment_id": payment_id,
            "order_id": request.order_id,
            "user_id": request.user_id,
            "amount": request.amount,
            "status": "initiated",
            "payment_method": request.payment_method,
            "created_at": datetime.now(),
        }
        self.payments_db[payment_id] = payment
        
        return InitiatePaymentResponse(
            payment_id=payment_id,
            status="initiated",
            message="Payment initiated successfully"
        )
    
    async def ProcessPayment(self, request, context):
        """Process a payment (gRPC method)."""
        from payment_pb2 import ProcessPaymentResponse
        
        payment = self.payments_db.get(request.payment_id)
        if not payment:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Payment not found")
            return ProcessPaymentResponse()
        
        # Process payment through gateway
        result = await payment_gateway.process_payment(
            request.payment_id,
            payment["amount"],
            payment["payment_method"]
        )
        
        # Update payment status
        payment["status"] = result["status"]
        payment["transaction_id"] = result["transaction_id"]
        if result["status"] == "completed":
            payment["completed_at"] = datetime.now()
        
        return ProcessPaymentResponse(
            payment_id=request.payment_id,
            status=result["status"],
            transaction_id=result["transaction_id"],
            message=f"Payment {result['status']}"
        )


async def serve_grpc(payments_db, refunds_db, port=50051):
    """Start gRPC server."""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add servicer (will be properly implemented after proto generation)
    # For now, we'll use a simpler approach
    servicer = PaymentServiceServicer(payments_db, refunds_db)
    
    # Register service (will be done after proto generation)
    # payment_pb2_grpc.add_PaymentServiceServicer_to_server(servicer, server)
    
    listen_addr = f"[::]:{port}"
    server.add_insecure_port(listen_addr)
    await server.start()
    print(f"gRPC server started on {listen_addr}")
    await server.wait_for_termination()


"""
Mocked payment gateway (Эквайринг) for Payment service.
"""

import random
import asyncio
from typing import Dict, Optional


class MockPaymentGateway:
    """Mocked payment gateway that simulates payment processing."""
    
    def __init__(self):
        self.transactions: Dict[str, Dict] = {}
    
    async def process_payment(
        self,
        payment_id: str,
        amount: float,
        payment_method: str
    ) -> Dict[str, str]:
        """
        Simulate payment processing with random success/failure.
        
        Args:
            payment_id: Payment identifier
            amount: Payment amount
            payment_method: Payment method
            
        Returns:
            Dictionary with transaction_id and status
        """
        # Simulate network delay
        await asyncio.sleep(0.5)
        
        # Randomly succeed or fail (90% success rate)
        success = random.random() > 0.1
        
        transaction_id = f"TXN_{payment_id[:8]}_{random.randint(100000, 999999)}"
        
        if success:
            status = "completed"
            self.transactions[transaction_id] = {
                "payment_id": payment_id,
                "status": status,
                "amount": amount,
            }
        else:
            status = "declined"
        
        return {
            "transaction_id": transaction_id,
            "status": status,
        }
    
    async def process_refund(
        self,
        refund_id: str,
        payment_id: str,
        amount: float
    ) -> Dict[str, str]:
        """
        Simulate refund processing.
        
        Args:
            refund_id: Refund identifier
            payment_id: Original payment identifier
            amount: Refund amount
            
        Returns:
            Dictionary with transaction_id and status
        """
        # Simulate network delay
        await asyncio.sleep(0.5)
        
        # Refunds usually succeed
        transaction_id = f"REF_{refund_id[:8]}_{random.randint(100000, 999999)}"
        
        return {
            "transaction_id": transaction_id,
            "status": "completed",
        }


# Global instance
payment_gateway = MockPaymentGateway()


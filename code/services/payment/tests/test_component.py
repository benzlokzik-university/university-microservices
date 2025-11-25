"""Component tests for Payment service.

These tests verify payment processing with mocked payment gateway.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_payment_gateway():
    """Mock payment gateway."""
    with patch("main.payment_gateway") as mock:
        yield mock


class TestPaymentComponent:
    """Component tests for payment operations."""
    
    def test_initiate_payment(self, client):
        """Test initiating a payment."""
        response = client.post(
            "/api/v1/payments",
            json={
                "order_id": "order-123",
                "user_id": "user-456",
                "amount": 1000.0,
                "payment_method": "card"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["order_id"] == "order-123"
        assert data["user_id"] == "user-456"
        assert data["amount"] == 1000.0
        assert data["status"] == "initiated"
        assert "payment_id" in data
    
    def test_process_payment_success(self, client, mock_payment_gateway):
        """Test processing a payment successfully."""
        # Initiate payment
        initiate_response = client.post(
            "/api/v1/payments",
            json={
                "order_id": "order-123",
                "user_id": "user-456",
                "amount": 1000.0,
                "payment_method": "card"
            }
        )
        payment_id = initiate_response.json()["payment_id"]
        
        # Mock successful payment processing
        mock_payment_gateway.process_payment = AsyncMock(return_value={
            "transaction_id": "TXN-123456",
            "status": "completed"
        })
        
        # Process payment
        response = client.post(
            f"/api/v1/payments/{payment_id}/process",
            json={
                "payment_id": payment_id,
                "transaction_id": "TXN-123456"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["transaction_id"] == "TXN-123456"
    
    def test_process_payment_declined(self, client, mock_payment_gateway):
        """Test processing a payment that gets declined."""
        # Initiate payment
        initiate_response = client.post(
            "/api/v1/payments",
            json={
                "order_id": "order-123",
                "user_id": "user-456",
                "amount": 1000.0,
                "payment_method": "card"
            }
        )
        payment_id = initiate_response.json()["payment_id"]
        
        # Mock declined payment
        mock_payment_gateway.process_payment = AsyncMock(return_value={
            "transaction_id": "TXN-789",
            "status": "declined"
        })
        
        # Process payment
        response = client.post(
            f"/api/v1/payments/{payment_id}/process",
            json={
                "payment_id": payment_id,
                "transaction_id": "TXN-789"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "declined"
    
    def test_request_refund(self, client):
        """Test requesting a refund."""
        # Create and process payment first
        initiate_response = client.post(
            "/api/v1/payments",
            json={
                "order_id": "order-123",
                "user_id": "user-456",
                "amount": 1000.0,
                "payment_method": "card"
            }
        )
        payment_id = initiate_response.json()["payment_id"]
        
        # Mock successful payment
        with patch("main.payment_gateway") as mock_gateway:
            mock_gateway.process_payment = AsyncMock(return_value={
                "transaction_id": "TXN-123",
                "status": "completed"
            })
            client.post(
                f"/api/v1/payments/{payment_id}/process",
                json={"payment_id": payment_id, "transaction_id": "TXN-123"}
            )
        
        # Request refund
        response = client.post(
            "/api/v1/refunds",
            json={
                "payment_id": payment_id,
                "user_id": "user-456",
                "reason": "Order cancellation",
                "amount": 1000.0
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["payment_id"] == payment_id
        assert data["status"] == "requested"
        assert data["reason"] == "Order cancellation"
    
    def test_get_payment(self, client):
        """Test getting payment information."""
        # Create payment
        create_response = client.post(
            "/api/v1/payments",
            json={
                "order_id": "order-123",
                "user_id": "user-456",
                "amount": 1000.0,
                "payment_method": "card"
            }
        )
        payment_id = create_response.json()["payment_id"]
        
        # Get payment
        response = client.get(f"/api/v1/payments/{payment_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["payment_id"] == payment_id
        assert data["amount"] == 1000.0


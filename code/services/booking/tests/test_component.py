"""Component tests for Booking service.

These tests verify the service works with mocked dependencies (User Account service).
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_user_service():
    """Mock user service responses."""
    with patch("main.validate_user") as mock:
        yield mock


class TestBookingComponent:
    """Component tests for booking operations."""
    
    def test_book_game_success(self, client, mock_user_service):
        """Test successful game booking with mocked user validation."""
        # Mock user validation to return True
        mock_user_service.return_value = True
        
        response = client.post(
            "/api/v1/bookings",
            json={
                "game_id": "game-123",
                "user_id": "user-456",
                "booking_date": "2024-01-20T10:00:00",
                "pickup_date": "2024-01-21T10:00:00"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["game_id"] == "game-123"
        assert data["user_id"] == "user-456"
        assert data["status"] == "pending"
        assert "booking_id" in data
        
        # Verify user validation was called
        mock_user_service.assert_called_once_with("user-456")
    
    def test_book_game_user_not_found(self, client, mock_user_service):
        """Test booking fails when user is not found or blocked."""
        # Mock user validation to return False
        mock_user_service.return_value = False
        
        response = client.post(
            "/api/v1/bookings",
            json={
                "game_id": "game-123",
                "user_id": "invalid-user",
                "booking_date": "2024-01-20T10:00:00",
                "pickup_date": "2024-01-21T10:00:00"
            }
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower() or "blocked" in response.json()["detail"].lower()
    
    def test_cancel_booking(self, client, mock_user_service):
        """Test canceling a booking."""
        # Mock user validation
        mock_user_service.return_value = True
        
        # Create booking
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "game_id": "game-123",
                "user_id": "user-456",
                "booking_date": "2024-01-20T10:00:00",
                "pickup_date": "2024-01-21T10:00:00"
            }
        )
        booking_id = create_response.json()["booking_id"]
        
        # Cancel booking
        response = client.post(
            f"/api/v1/bookings/{booking_id}/cancel",
            json={
                "user_id": "user-456",
                "reason": "Change of plans"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "canceled"
    
    def test_get_booking(self, client, mock_user_service):
        """Test getting booking information."""
        # Mock user validation
        mock_user_service.return_value = True
        
        # Create booking
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "game_id": "game-123",
                "user_id": "user-456",
                "booking_date": "2024-01-20T10:00:00",
                "pickup_date": "2024-01-21T10:00:00"
            }
        )
        booking_id = create_response.json()["booking_id"]
        
        # Get booking
        response = client.get(f"/api/v1/bookings/{booking_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["booking_id"] == booking_id
        assert data["game_id"] == "game-123"
        assert data["user_id"] == "user-456"
    
    def test_cancel_booking_wrong_user(self, client, mock_user_service):
        """Test canceling booking fails for wrong user."""
        # Mock user validation
        mock_user_service.return_value = True
        
        # Create booking
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "game_id": "game-123",
                "user_id": "user-456",
                "booking_date": "2024-01-20T10:00:00",
                "pickup_date": "2024-01-21T10:00:00"
            }
        )
        booking_id = create_response.json()["booking_id"]
        
        # Try to cancel with wrong user
        response = client.post(
            f"/api/v1/bookings/{booking_id}/cancel",
            json={
                "user_id": "wrong-user",
                "reason": "Test"
            }
        )
        assert response.status_code == 403


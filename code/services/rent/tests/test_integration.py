"""Integration tests for Rent service."""

from unittest.mock import patch
from fastapi import status
from datetime import datetime

from schemas import BookingResponse


class TestRentIntegration:
    """Integration tests for rent operations."""

    def test_create_order(self, client):
        """Test creating a rental order with mocked dependencies."""
        with (
            patch("main.get_booking") as mock_booking,
            patch("main.initiate_payment_grpc") as mock_payment,
        ):
            # Mock booking response
            mock_booking.return_value = BookingResponse(
                booking_id="booking-123",
                game_id="game-456",
                user_id="user-789",
                status="confirmed",
                pickup_date=datetime.now(),
            )

            # Mock payment response
            mock_payment.return_value = {"payment_id": "pay-123", "status": "initiated"}

            response = client.post(
                "/api/v1/orders",
                json={
                    "booking_id": "booking-123",
                    "user_id": "user-789",
                    "pickup_location": "Москва, ул. Тестовая, д. 1",
                    "rental_days": 7,
                },
            )
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["booking_id"] == "booking-123"
            assert data["game_id"] == "game-456"
            assert data["user_id"] == "user-789"
            assert data["status"] == "created"
            assert data["rental_days"] == 7
            assert "order_id" in data

    def test_confirm_receipt(self, client):
        """Test confirming game receipt."""
        # Create order first
        with (
            patch("main.get_booking") as mock_booking,
            patch("main.initiate_payment_grpc") as mock_payment,
        ):
            mock_booking.return_value = BookingResponse(
                booking_id="booking-123",
                game_id="game-456",
                user_id="user-789",
                status="confirmed",
                pickup_date=datetime.now(),
            )
            mock_payment.return_value = {"payment_id": "pay-123", "status": "initiated"}

            create_response = client.post(
                "/api/v1/orders",
                json={
                    "booking_id": "booking-123",
                    "user_id": "user-789",
                    "pickup_location": "Москва",
                    "rental_days": 7,
                },
            )
            order_id = create_response.json()["order_id"]

            # Confirm receipt
            response = client.post(
                f"/api/v1/orders/{order_id}/confirm-receipt",
                json={"user_id": "user-789"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "active"

    def test_return_game(self, client):
        """Test returning a game."""
        # Create order and confirm receipt
        with (
            patch("main.get_booking") as mock_booking,
            patch("main.initiate_payment_grpc") as mock_payment,
        ):
            mock_booking.return_value = BookingResponse(
                booking_id="booking-123",
                game_id="game-456",
                user_id="user-789",
                status="confirmed",
                pickup_date=datetime.now(),
            )
            mock_payment.return_value = {"payment_id": "pay-123", "status": "initiated"}

            create_response = client.post(
                "/api/v1/orders",
                json={
                    "booking_id": "booking-123",
                    "user_id": "user-789",
                    "pickup_location": "Москва",
                    "rental_days": 7,
                },
            )
            order_id = create_response.json()["order_id"]

            # Confirm receipt
            client.post(
                f"/api/v1/orders/{order_id}/confirm-receipt",
                json={"user_id": "user-789"},
            )

            # Return game
            response = client.post(
                f"/api/v1/orders/{order_id}/return",
                json={
                    "user_id": "user-789",
                    "return_location": "Москва, ул. Возврата, д. 1",
                },
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "returned"
            assert data["return_date"] is not None

    def test_charge_penalty(self, client):
        """Test charging a penalty."""
        # Create order
        with (
            patch("main.get_booking") as mock_booking,
            patch("main.initiate_payment_grpc") as mock_payment,
        ):
            mock_booking.return_value = BookingResponse(
                booking_id="booking-123",
                game_id="game-456",
                user_id="user-789",
                status="confirmed",
                pickup_date=datetime.now(),
            )
            mock_payment.return_value = {"payment_id": "pay-123", "status": "initiated"}

            create_response = client.post(
                "/api/v1/orders",
                json={
                    "booking_id": "booking-123",
                    "user_id": "user-789",
                    "pickup_location": "Москва",
                    "rental_days": 7,
                },
            )
            order_id = create_response.json()["order_id"]

            # Charge penalty
            response = client.post(
                f"/api/v1/orders/{order_id}/penalty",
                json={"penalty_amount": 200.0, "reason": "Late return"},
            )
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["penalty_amount"] == 200.0

    def test_get_order(self, client):
        """Test getting order information."""
        # Create order
        with (
            patch("main.get_booking") as mock_booking,
            patch("main.initiate_payment_grpc") as mock_payment,
        ):
            mock_booking.return_value = BookingResponse(
                booking_id="booking-123",
                game_id="game-456",
                user_id="user-789",
                status="confirmed",
                pickup_date=datetime.now(),
            )
            mock_payment.return_value = {"payment_id": "pay-123", "status": "initiated"}

            create_response = client.post(
                "/api/v1/orders",
                json={
                    "booking_id": "booking-123",
                    "user_id": "user-789",
                    "pickup_location": "Москва",
                    "rental_days": 7,
                },
            )
            order_id = create_response.json()["order_id"]

            # Get order
            response = client.get(f"/api/v1/orders/{order_id}")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["order_id"] == order_id
            assert data["booking_id"] == "booking-123"

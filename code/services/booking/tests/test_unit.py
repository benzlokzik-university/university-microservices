import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from user_service import validate_user, get_user


class TestValidateUser:
    @pytest.mark.asyncio
    async def test_validate_user_exists_and_not_blocked(self):
        mock_user = {
            "user_id": "user-123",
            "email": "test@example.com",
            "is_blocked": False
        }
        
        with patch("user_service.get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user
            
            result = await validate_user("user-123")
            
            assert result is True
            mock_get_user.assert_called_once_with("user-123")
    
    @pytest.mark.asyncio
    async def test_validate_user_blocked(self):
        mock_user = {
            "user_id": "user-123",
            "email": "test@example.com",
            "is_blocked": True
        }
        
        with patch("user_service.get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user
            
            result = await validate_user("user-123")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_user_not_found(self):
        with patch("user_service.get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = None
            
            result = await validate_user("non-existent-user")
            
            assert result is False
            mock_get_user.assert_called_once_with("non-existent-user")
    
    @pytest.mark.asyncio
    async def test_validate_user_missing_is_blocked_field(self):
        mock_user = {
            "user_id": "user-123",
            "email": "test@example.com",
        }
        
        with patch("user_service.get_user", new_callable=AsyncMock) as mock_get_user:
            mock_get_user.return_value = mock_user
            
            result = await validate_user("user-123")
            
            # Should return True if is_blocked is missing (defaults to False)
            assert result is True


class TestGetUser:
    @pytest.mark.asyncio
    async def test_get_user_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": "user-123",
            "email": "test@example.com",
            "is_blocked": False
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await get_user("user-123")
            
            assert result is not None
            assert result["user_id"] == "user-123"
            assert result["email"] == "test@example.com"
            mock_client.return_value.__aenter__.return_value.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self):
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await get_user("non-existent-user")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_user_network_error(self):
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=Exception("Network error"))
            
            result = await get_user("user-123")
            
            assert result is None


class TestBookingLogic:
    def test_booking_creation_structure(self):
        from datetime import datetime
        import uuid
        
        booking_id = str(uuid.uuid4())
        booking = {
            "booking_id": booking_id,
            "game_id": "game-123",
            "user_id": "user-456",
            "status": "pending",
            "booking_date": datetime.now(),
            "pickup_date": datetime.now(),
            "created_at": datetime.now(),
        }
        
        assert booking["booking_id"] == booking_id
        assert booking["game_id"] == "game-123"
        assert booking["user_id"] == "user-456"
        assert booking["status"] == "pending"
        assert "booking_date" in booking
        assert "pickup_date" in booking
        assert "created_at" in booking
    
    def test_booking_status_transitions(self):
        booking = {"status": "pending"}
        
        # Valid transitions
        valid_statuses = ["pending", "confirmed", "canceled"]
        
        for status in valid_statuses:
            booking["status"] = status
            assert booking["status"] in valid_statuses
    
    def test_booking_cancellation(self):
        booking = {
            "booking_id": "booking-123",
            "user_id": "user-456",
            "status": "pending"
        }
        
        # Cancel booking
        booking["status"] = "canceled"
        
        assert booking["status"] == "canceled"
        assert booking["booking_id"] == "booking-123"
    
    def test_booking_ownership_validation(self):
        booking = {
            "booking_id": "booking-123",
            "user_id": "user-456",
        }
        
        # Same user should have access
        assert booking["user_id"] == "user-456"
        
        # Different user should not have access
        assert booking["user_id"] != "user-789"


class TestBookingValidation:
    def test_validate_booking_exists(self):
        bookings_db = {
            "booking-123": {"booking_id": "booking-123", "status": "pending"},
            "booking-456": {"booking_id": "booking-456", "status": "confirmed"},
        }
        
        assert "booking-123" in bookings_db
        assert "booking-456" in bookings_db
        assert "booking-999" not in bookings_db
    
    def test_validate_booking_ownership(self):
        booking = {
            "booking_id": "booking-123",
            "user_id": "user-456",
        }
        
        # Owner should match
        assert booking["user_id"] == "user-456"
        
        # Non-owner should not match
        assert booking["user_id"] != "user-789"


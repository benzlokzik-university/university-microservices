"""Component tests for Rating service.

These tests verify rating and comment functionality with mocked Perspective API.
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
def mock_perspective_api():
    """Mock Perspective API."""
    with patch("main.perspective_api") as mock:
        yield mock


class TestRatingComponent:
    """Component tests for rating operations."""
    
    def test_leave_rating(self, client, mock_perspective_api):
        """Test leaving a rating for a game."""
        with patch("main.update_game_rating") as mock_update:
            mock_update.return_value = None
            
            response = client.post(
                "/api/v1/ratings",
                json={
                    "game_id": "game-123",
                    "user_id": "user-456",
                    "rating": 5
                }
            )
            assert response.status_code == 201
            data = response.json()
            assert data["game_id"] == "game-123"
            assert data["user_id"] == "user-456"
            assert data["rating"] == 5
            assert "rating_id" in data
    
    def test_leave_comment_approved(self, client, mock_perspective_api):
        """Test leaving a comment that gets approved by moderation."""
        # Mock Perspective API to return non-toxic comment
        mock_perspective_api.analyze_comment = AsyncMock(return_value=(
            False,  # is_moderated
            {"toxicity": 0.2, "spam": 0.1, "profanity": 0.0}
        ))
        
        response = client.post(
            "/api/v1/comments",
            json={
                "game_id": "game-123",
                "user_id": "user-456",
                "comment_text": "Great game! Highly recommend it."
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["game_id"] == "game-123"
        assert data["user_id"] == "user-456"
        assert data["comment_text"] == "Great game! Highly recommend it."
        assert data["is_moderated"] is False
    
    def test_leave_comment_toxic(self, client, mock_perspective_api):
        """Test leaving a toxic comment that gets moderated."""
        # Mock Perspective API to return toxic comment
        mock_perspective_api.analyze_comment = AsyncMock(return_value=(
            True,  # is_moderated
            {"toxicity": 0.8, "spam": 0.1, "profanity": 0.3}
        ))
        
        response = client.post(
            "/api/v1/comments",
            json={
                "game_id": "game-123",
                "user_id": "user-456",
                "comment_text": "This game is bad and terrible"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["is_moderated"] is True
    
    def test_get_rating(self, client):
        """Test getting rating information."""
        # Create rating first
        with patch("main.update_game_rating") as mock_update:
            mock_update.return_value = None
            
            create_response = client.post(
                "/api/v1/ratings",
                json={
                    "game_id": "game-123",
                    "user_id": "user-456",
                    "rating": 4
                }
            )
            rating_id = create_response.json()["rating_id"]
            
            # Get rating
            response = client.get(f"/api/v1/ratings/{rating_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["rating_id"] == rating_id
            assert data["rating"] == 4
    
    def test_get_comment(self, client, mock_perspective_api):
        """Test getting comment information."""
        # Mock Perspective API
        mock_perspective_api.analyze_comment = AsyncMock(return_value=(
            False,
            {"toxicity": 0.1, "spam": 0.1, "profanity": 0.0}
        ))
        
        # Create comment
        create_response = client.post(
            "/api/v1/comments",
            json={
                "game_id": "game-123",
                "user_id": "user-456",
                "comment_text": "Nice game"
            }
        )
        comment_id = create_response.json()["comment_id"]
        
        # Get comment
        response = client.get(f"/api/v1/comments/{comment_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["comment_id"] == comment_id
        assert data["comment_text"] == "Nice game"


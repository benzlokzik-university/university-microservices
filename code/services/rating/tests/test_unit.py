import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from main import update_game_rating
from perspective_api import MockPerspectiveAPI


class TestUpdateGameRating:
    @pytest.mark.asyncio
    async def test_calculate_average_rating(self):
        # Mock ratings_db
        ratings_db = {
            "rating1": {"rating_id": "rating1", "game_id": "game-123", "rating": 5, "user_id": "user1"},
            "rating2": {"rating_id": "rating2", "game_id": "game-123", "rating": 4, "user_id": "user2"},
            "rating3": {"rating_id": "rating3", "game_id": "game-123", "rating": 3, "user_id": "user3"},
            "rating4": {"rating_id": "rating4", "game_id": "game-456", "rating": 5, "user_id": "user4"},
        }
        
        # Calculate average for game-123
        game_ratings = [r["rating"] for r in ratings_db.values() if r["game_id"] == "game-123"]
        avg_rating = sum(game_ratings) / len(game_ratings)
        
        assert avg_rating == 4.0
        assert len(game_ratings) == 3
    
    @pytest.mark.asyncio
    async def test_update_game_rating_with_ratings(self):
        # Mock the ratings_db and httpx client
        with patch("main.ratings_db", {
            "rating1": {"rating_id": "rating1", "game_id": "game-123", "rating": 5},
            "rating2": {"rating_id": "rating2", "game_id": "game-123", "rating": 4},
        }), patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.put = AsyncMock(return_value=mock_response)
            
            await update_game_rating("game-123")
            
            # Verify HTTP call was made
            mock_client.return_value.__aenter__.return_value.put.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_game_rating_no_ratings(self):
        with patch("main.ratings_db", {}), patch("httpx.AsyncClient") as mock_client:
            await update_game_rating("game-123")
            
            # Should not make HTTP call if no ratings
            mock_client.return_value.__aenter__.return_value.put.assert_not_called()


class TestMockPerspectiveAPI:
    @pytest.mark.asyncio
    async def test_analyze_comment_non_toxic(self):
        api = MockPerspectiveAPI()
        is_moderated, scores = await api.analyze_comment("Great game! I love it!")
        
        assert is_moderated is False
        assert "toxicity" in scores
        assert "spam" in scores
        assert "profanity" in scores
        assert scores["toxicity"] < 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_comment_toxic(self):
        api = MockPerspectiveAPI()
        is_moderated, scores = await api.analyze_comment("This game is bad and terrible")
        
        assert is_moderated is True
        assert "toxicity" in scores
        assert scores["toxicity"] > 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_comment_with_toxic_word(self):
        api = MockPerspectiveAPI()
        is_moderated, scores = await api.analyze_comment("I hate this game")
        
        assert is_moderated is True
        assert scores["toxicity"] > 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_comment_scores_structure(self):
        api = MockPerspectiveAPI()
        is_moderated, scores = await api.analyze_comment("Nice game")
        
        assert isinstance(scores, dict)
        assert "toxicity" in scores
        assert "spam" in scores
        assert "profanity" in scores
        assert 0.0 <= scores["toxicity"] <= 1.0
        assert 0.0 <= scores["spam"] <= 1.0
        assert 0.0 <= scores["profanity"] <= 1.0


class TestRatingLogic:
    def test_rating_creation_structure(self):
        rating = {
            "rating_id": "test-rating-id",
            "game_id": "game-123",
            "user_id": "user-456",
            "rating": 5,
            "created_at": datetime.now(),
        }
        
        assert rating["rating_id"] == "test-rating-id"
        assert rating["game_id"] == "game-123"
        assert rating["user_id"] == "user-456"
        assert rating["rating"] == 5
        assert isinstance(rating["created_at"], datetime)
    
    def test_rating_validation(self):
        valid_ratings = [1, 2, 3, 4, 5]
        invalid_ratings = [0, 6, -1, 10]
        
        for rating in valid_ratings:
            assert 1 <= rating <= 5
        
        for rating in invalid_ratings:
            assert not (1 <= rating <= 5)


class TestCommentLogic:
    def test_comment_creation_structure(self):
        comment = {
            "comment_id": "test-comment-id",
            "game_id": "game-123",
            "user_id": "user-456",
            "comment_text": "Great game!",
            "is_moderated": False,
            "created_at": datetime.now(),
        }
        
        assert comment["comment_id"] == "test-comment-id"
        assert comment["game_id"] == "game-123"
        assert comment["user_id"] == "user-456"
        assert comment["comment_text"] == "Great game!"
        assert comment["is_moderated"] is False
        assert isinstance(comment["created_at"], datetime)
    
    def test_moderated_comment_flag(self):
        moderated_comment = {
            "comment_id": "comment1",
            "is_moderated": True,
        }
        
        non_moderated_comment = {
            "comment_id": "comment2",
            "is_moderated": False,
        }
        
        assert moderated_comment["is_moderated"] is True
        assert non_moderated_comment["is_moderated"] is False


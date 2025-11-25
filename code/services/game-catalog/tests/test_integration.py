"""Integration tests for Game Catalog service."""

import pytest
from fastapi import status


class TestGameManagement:
    """Integration tests for game management."""

    def test_add_game(self, client):
        """Test adding a new game to catalog."""
        response = client.post(
            "/api/v1/games",
            json={
                "name": "Каркассон",
                "description": "Стратегическая настольная игра",
                "min_players": 2,
                "max_players": 5,
                "play_time_minutes": 45,
                "age_rating": 7,
                "category": "Стратегия",
                "price_per_day": 150.0,
                "total_copies": 10,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Каркассон"
        assert data["status"] == "available"
        assert data["available_count"] == 10
        assert data["total_copies"] == 10
        assert "game_id" in data

    def test_get_game(self, client):
        """Test getting game information."""
        # Add game first
        add_response = client.post(
            "/api/v1/games",
            json={
                "name": "Монополия",
                "min_players": 2,
                "max_players": 8,
                "price_per_day": 200.0,
                "total_copies": 5,
            },
        )
        game_id = add_response.json()["game_id"]

        # Get game
        response = client.get(f"/api/v1/games/{game_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["game_id"] == game_id
        assert data["name"] == "Монополия"

    def test_update_game(self, client):
        """Test updating game information."""
        # Add game
        add_response = client.post(
            "/api/v1/games",
            json={
                "name": "Шахматы",
                "min_players": 2,
                "max_players": 2,
                "price_per_day": 100.0,
                "total_copies": 3,
            },
        )
        game_id = add_response.json()["game_id"]

        # Update game
        response = client.put(
            f"/api/v1/games/{game_id}",
            json={"name": "Шахматы (обновленные)", "price_per_day": 120.0},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Шахматы (обновленные)"
        assert data["price_per_day"] == 120.0

    def test_search_games(self, client):
        """Test searching games."""
        # Add multiple games
        client.post(
            "/api/v1/games",
            json={
                "name": "Стратегия 1",
                "category": "Стратегия",
                "min_players": 2,
                "max_players": 4,
                "price_per_day": 150.0,
                "total_copies": 5,
            },
        )
        client.post(
            "/api/v1/games",
            json={
                "name": "Другая игра",
                "category": "Другое",
                "min_players": 1,
                "max_players": 2,
                "price_per_day": 200.0,
                "total_copies": 3,
            },
        )

        # Search by category
        response = client.post("/api/v1/games/search", json={"category": "Стратегия"})
        assert response.status_code == status.HTTP_200_OK
        games = response.json()
        assert len(games) >= 1
        assert all(game["category"] == "Стратегия" for game in games)

    def test_update_availability(self, client):
        """Test updating game availability."""
        # Add game
        add_response = client.post(
            "/api/v1/games",
            json={
                "name": "Тестовая игра",
                "min_players": 2,
                "max_players": 4,
                "price_per_day": 100.0,
                "total_copies": 10,
            },
        )
        game_id = add_response.json()["game_id"]

        # Update availability
        response = client.patch(
            f"/api/v1/games/{game_id}/availability", json={"available_count": 5}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["available_count"] == 5
        assert data["status"] == "available"

        # Set to 0 - should mark as unavailable
        response = client.patch(
            f"/api/v1/games/{game_id}/availability", json={"available_count": 0}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["available_count"] == 0
        assert data["status"] == "unavailable"

"""Integration tests for User Account service.

These tests verify the service works with a real database (SQLite in-memory for testing).
"""

import pytest
from fastapi import status


class TestUserRegistration:
    """Integration tests for user registration."""
    
    def test_register_user_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/users/register",
            json={
                "email": "test@example.com",
                "password": "securepassword123",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+79991234567"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["phone"] == "+79991234567"
        assert data["is_blocked"] is False
        assert "user_id" in data
        assert "created_at" in data
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email fails."""
        # Register first user
        client.post(
            "/api/v1/users/register",
            json={
                "email": "duplicate@example.com",
                "password": "password123",
                "first_name": "First",
                "last_name": "User"
            }
        )
        
        # Try to register with same email
        response = client.post(
            "/api/v1/users/register",
            json={
                "email": "duplicate@example.com",
                "password": "password123",
                "first_name": "Second",
                "last_name": "User"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()


class TestUserAuthorization:
    """Integration tests for user authorization."""
    
    def test_authorize_success(self, client):
        """Test successful user authorization."""
        # Register user first
        register_response = client.post(
            "/api/v1/users/register",
            json={
                "email": "auth@example.com",
                "password": "testpassword123",
                "first_name": "Auth",
                "last_name": "User"
            }
        )
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Authorize
        response = client.post(
            "/api/v1/users/authorize",
            json={
                "email": "auth@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "auth@example.com"
    
    def test_authorize_invalid_password(self, client):
        """Test authorization with invalid password."""
        # Register user
        client.post(
            "/api/v1/users/register",
            json={
                "email": "invalid@example.com",
                "password": "correctpassword",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        # Try to authorize with wrong password
        response = client.post(
            "/api/v1/users/authorize",
            json={
                "email": "invalid@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_authorize_blocked_user(self, client):
        """Test authorization fails for blocked user."""
        # Register user
        register_response = client.post(
            "/api/v1/users/register",
            json={
                "email": "blocked@example.com",
                "password": "password123",
                "first_name": "Blocked",
                "last_name": "User"
            }
        )
        user_id = register_response.json()["user_id"]
        
        # Block user
        client.post(
            f"/api/v1/users/{user_id}/block",
            json={"reason": "Test blocking"}
        )
        
        # Try to authorize
        response = client.post(
            "/api/v1/users/authorize",
            json={
                "email": "blocked@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserProfile:
    """Integration tests for user profile management."""
    
    def test_get_user(self, client):
        """Test getting user information."""
        # Register user
        register_response = client.post(
            "/api/v1/users/register",
            json={
                "email": "get@example.com",
                "password": "password123",
                "first_name": "Get",
                "last_name": "User"
            }
        )
        user_id = register_response.json()["user_id"]
        
        # Get user
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == user_id
        assert data["email"] == "get@example.com"
    
    def test_update_profile(self, client):
        """Test updating user profile."""
        # Register user
        register_response = client.post(
            "/api/v1/users/register",
            json={
                "email": "update@example.com",
                "password": "password123",
                "first_name": "Old",
                "last_name": "Name"
            }
        )
        user_id = register_response.json()["user_id"]
        
        # Update profile
        response = client.put(
            f"/api/v1/users/{user_id}/profile",
            json={
                "first_name": "New",
                "last_name": "Name",
                "phone": "+79999999999"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "New"
        assert data["last_name"] == "Name"
        assert data["phone"] == "+79999999999"
    
    def test_block_user(self, client):
        """Test blocking a user."""
        # Register user
        register_response = client.post(
            "/api/v1/users/register",
            json={
                "email": "block@example.com",
                "password": "password123",
                "first_name": "Block",
                "last_name": "User"
            }
        )
        user_id = register_response.json()["user_id"]
        
        # Block user
        response = client.post(
            f"/api/v1/users/{user_id}/block",
            json={"reason": "Violation of terms"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_blocked"] is True
        
        # Verify user is blocked
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.json()["is_blocked"] is True


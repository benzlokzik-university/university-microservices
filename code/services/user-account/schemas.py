"""
Pydantic schemas for User Account service.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterUserRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class AuthorizeUserRequest(BaseModel):
    """Request schema for user authorization."""

    email: EmailStr
    password: str


class UpdateUserProfileRequest(BaseModel):
    """Request schema for updating user profile."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class BlockUserRequest(BaseModel):
    """Request schema for blocking user."""

    reason: Optional[str] = Field(None, max_length=500)


class UserResponse(BaseModel):
    """Response schema for user information."""

    user_id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]
    is_blocked: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Response schema for authorization."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse

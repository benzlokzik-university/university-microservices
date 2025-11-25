"""
Pydantic schemas for Rating service.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LeaveRatingRequest(BaseModel):
    """Request schema for leaving a rating."""
    game_id: str
    user_id: str
    rating: int = Field(..., ge=1, le=5)


class LeaveCommentRequest(BaseModel):
    """Request schema for leaving a comment."""
    game_id: str
    user_id: str
    comment_text: str = Field(..., min_length=1, max_length=2000)


class UpdateGameRatingRequest(BaseModel):
    """Request schema for updating game rating (system command)."""
    game_id: str
    new_rating: float = Field(..., ge=0, le=5)


class RatingResponse(BaseModel):
    """Response schema for rating information."""
    rating_id: str
    game_id: str
    user_id: str
    rating: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentResponse(BaseModel):
    """Response schema for comment information."""
    comment_id: str
    game_id: str
    user_id: str
    comment_text: str
    is_moderated: bool
    created_at: datetime

    model_config = {"from_attributes": True}


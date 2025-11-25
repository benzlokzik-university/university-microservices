"""
Pydantic schemas for Game Catalog service.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class AddGameRequest(BaseModel):
    """Request schema for adding a game."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    min_players: int = Field(..., ge=1, le=20)
    max_players: int = Field(..., ge=1, le=50)
    play_time_minutes: Optional[int] = Field(None, ge=1)
    age_rating: Optional[int] = Field(None, ge=0, le=18)
    category: Optional[str] = Field(None, max_length=100)
    price_per_day: float = Field(..., ge=0)
    total_copies: int = Field(..., ge=1)


class UpdateGameInfoRequest(BaseModel):
    """Request schema for updating game information."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    min_players: Optional[int] = Field(None, ge=1, le=20)
    max_players: Optional[int] = Field(None, ge=1, le=50)
    play_time_minutes: Optional[int] = Field(None, ge=1)
    age_rating: Optional[int] = Field(None, ge=0, le=18)
    category: Optional[str] = Field(None, max_length=100)
    price_per_day: Optional[float] = Field(None, ge=0)


class UpdateAvailableGamesRequest(BaseModel):
    """Request schema for updating available games count."""

    available_count: int = Field(..., ge=0)


class FindGameRequest(BaseModel):
    """Request schema for searching games."""

    query: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    min_players: Optional[int] = Field(None, ge=1)
    max_players: Optional[int] = Field(None, ge=1)
    max_price: Optional[float] = Field(None, ge=0)


class GameResponse(BaseModel):
    """Response schema for game information."""

    game_id: str
    name: str
    description: Optional[str]
    status: str
    available_count: int
    total_copies: int
    photo_urls: List[str]
    rating: Optional[float]
    min_players: int
    max_players: int
    play_time_minutes: Optional[int]
    age_rating: Optional[int]
    category: Optional[str]
    price_per_day: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

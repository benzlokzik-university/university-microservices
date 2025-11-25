"""
Game Catalog Service - FastAPI application.

This service handles game catalog management, search, and availability tracking.
"""

from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from contextlib import asynccontextmanager
import uvicorn

from database import get_db, engine, Base
from models import Game
from schemas import (
    AddGameRequest,
    UpdateGameInfoRequest,
    UpdateAvailableGamesRequest,
    FindGameRequest,
    GameResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    # Startup - create tables
    print("🚀 Game Catalog service starting up...")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    print("🛑 Game Catalog service shutting down...")


app = FastAPI(
    title="Game Catalog Service",
    description="Service for managing game catalog, search, and availability",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/api/v1/games",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Games"],
    summary="Add a new game to catalog",
)
async def add_game(request: AddGameRequest, db: Session = Depends(get_db)):
    """Add a new game to the catalog."""
    db_game = Game(
        name=request.name,
        description=request.description,
        min_players=request.min_players,
        max_players=request.max_players,
        play_time_minutes=request.play_time_minutes,
        age_rating=request.age_rating,
        category=request.category,
        price_per_day=request.price_per_day,
        total_copies=request.total_copies,
        available_count=request.total_copies,
        status="available",
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    
    return GameResponse.model_validate(db_game)


@app.get(
    "/api/v1/games/{game_id}",
    response_model=GameResponse,
    tags=["Games"],
    summary="Get game information",
)
async def get_game(game_id: str, db: Session = Depends(get_db)):
    """Get game information by ID."""
    game = db.query(Game).filter(Game.game_id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return GameResponse.model_validate(game)


@app.put(
    "/api/v1/games/{game_id}",
    response_model=GameResponse,
    tags=["Games"],
    summary="Update game information",
)
async def update_game_info(
    game_id: str,
    request: UpdateGameInfoRequest,
    db: Session = Depends(get_db)
):
    """Update game information."""
    game = db.query(Game).filter(Game.game_id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Update fields if provided
    if request.name is not None:
        game.name = request.name
    if request.description is not None:
        game.description = request.description
    if request.min_players is not None:
        game.min_players = request.min_players
    if request.max_players is not None:
        game.max_players = request.max_players
    if request.play_time_minutes is not None:
        game.play_time_minutes = request.play_time_minutes
    if request.age_rating is not None:
        game.age_rating = request.age_rating
    if request.category is not None:
        game.category = request.category
    if request.price_per_day is not None:
        game.price_per_day = request.price_per_day
    
    db.commit()
    db.refresh(game)
    
    return GameResponse.model_validate(game)


@app.post(
    "/api/v1/games/search",
    response_model=list[GameResponse],
    tags=["Games"],
    summary="Search games",
)
async def search_games(request: FindGameRequest, db: Session = Depends(get_db)):
    """Search games by various criteria."""
    query = db.query(Game)
    
    # Apply filters
    filters = []
    
    if request.query:
        filters.append(
            or_(
                Game.name.ilike(f"%{request.query}%"),
                Game.description.ilike(f"%{request.query}%")
            )
        )
    
    if request.category:
        filters.append(Game.category == request.category)
    
    if request.min_players:
        filters.append(Game.max_players >= request.min_players)
    
    if request.max_players:
        filters.append(Game.min_players <= request.max_players)
    
    if request.max_price:
        filters.append(Game.price_per_day <= request.max_price)
    
    if filters:
        query = query.filter(and_(*filters))
    
    games = query.all()
    return [GameResponse.model_validate(game) for game in games]


@app.patch(
    "/api/v1/games/{game_id}/availability",
    response_model=GameResponse,
    tags=["Games"],
    summary="Update available games count",
)
async def update_available_games(
    game_id: str,
    request: UpdateAvailableGamesRequest,
    db: Session = Depends(get_db)
):
    """Update the number of available game copies."""
    game = db.query(Game).filter(Game.game_id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    if request.available_count > game.total_copies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Available count cannot exceed total copies"
        )
    
    game.available_count = request.available_count
    
    # Update status based on availability
    if game.available_count == 0:
        game.status = "unavailable"
    elif game.status == "unavailable" and game.available_count > 0:
        game.status = "available"
    
    db.commit()
    db.refresh(game)
    
    return GameResponse.model_validate(game)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "game-catalog"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )

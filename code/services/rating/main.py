"""
Rating Service - FastAPI application.

This service handles game ratings and comments. It includes:
- Mocked Perspective API for content moderation
- RabbitMQ for publishing domain events
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn
import uuid
import httpx

from schemas import (
    LeaveRatingRequest,
    LeaveCommentRequest,
    UpdateGameRatingRequest,
    RatingResponse,
    CommentResponse,
)
from perspective_api import perspective_api
from rabbitmq_client import publish_event

# In-memory storage (in production, use a database)
ratings_db = {}
comments_db = {}

# External service URL
GAME_CATALOG_SERVICE_URL = "http://game-catalog:8002"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    print("🚀 Rating service starting up...")
    yield
    print("🛑 Rating service shutting down...")


app = FastAPI(
    title="Rating Service",
    description="Service for managing game ratings and comments with content moderation",
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


async def update_game_rating(game_id: str):
    """Update game rating in Game Catalog service."""
    # Calculate average rating
    game_ratings = [r["rating"] for r in ratings_db.values() if r["game_id"] == game_id]
    if game_ratings:
        avg_rating = sum(game_ratings) / len(game_ratings)

        # Update in Game Catalog service
        async with httpx.AsyncClient() as client:
            try:
                await client.put(
                    f"{GAME_CATALOG_SERVICE_URL}/api/v1/games/{game_id}",
                    json={"rating": avg_rating},
                )
            except Exception as e:
                print(f"Error updating game rating: {e}")


@app.post(
    "/api/v1/ratings",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Ratings"],
    summary="Leave a rating",
)
async def leave_rating(request: LeaveRatingRequest):
    """Leave a rating for a game."""
    rating_id = str(uuid.uuid4())

    rating = {
        "rating_id": rating_id,
        "game_id": request.game_id,
        "user_id": request.user_id,
        "rating": request.rating,
        "created_at": datetime.now(),
    }

    ratings_db[rating_id] = rating

    # Update game rating in Game Catalog
    await update_game_rating(request.game_id)

    # Publish domain event
    await publish_event(
        "rating.left",
        {
            "rating_id": rating_id,
            "game_id": request.game_id,
            "user_id": request.user_id,
            "rating": request.rating,
        },
    )

    return RatingResponse(**rating)


@app.post(
    "/api/v1/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Comments"],
    summary="Leave a comment",
)
async def leave_comment(request: LeaveCommentRequest):
    """Leave a comment for a game (with content moderation)."""
    # Analyze comment via mocked Perspective API
    is_moderated, scores = await perspective_api.analyze_comment(request.comment_text)

    comment_id = str(uuid.uuid4())

    comment = {
        "comment_id": comment_id,
        "game_id": request.game_id,
        "user_id": request.user_id,
        "comment_text": request.comment_text,
        "is_moderated": is_moderated,
        "created_at": datetime.now(),
    }

    comments_db[comment_id] = comment

    # Publish domain event
    await publish_event(
        "comment.left",
        {
            "comment_id": comment_id,
            "game_id": request.game_id,
            "user_id": request.user_id,
            "is_moderated": is_moderated,
        },
    )

    return CommentResponse(**comment)


@app.put(
    "/api/v1/games/{game_id}/rating",
    response_model=dict,
    tags=["Ratings"],
    summary="Update game rating (system command)",
)
async def update_game_rating_endpoint(game_id: str, request: UpdateGameRatingRequest):
    """Update game rating (system command)."""
    # This would typically be called by an event handler
    # For now, we'll just acknowledge it

    # Publish domain event
    await publish_event(
        "rating.updated",
        {
            "game_id": game_id,
            "new_rating": request.new_rating,
        },
    )

    return {"success": True, "message": "Game rating updated"}


@app.get(
    "/api/v1/ratings/{rating_id}",
    response_model=RatingResponse,
    tags=["Ratings"],
    summary="Get rating information",
)
async def get_rating(rating_id: str):
    """Get rating information by ID."""
    rating = ratings_db.get(rating_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found"
        )
    return RatingResponse(**rating)


@app.get(
    "/api/v1/comments/{comment_id}",
    response_model=CommentResponse,
    tags=["Comments"],
    summary="Get comment information",
)
async def get_comment(comment_id: str):
    """Get comment information by ID."""
    comment = comments_db.get(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    return CommentResponse(**comment)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "rating"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8006, reload=True)

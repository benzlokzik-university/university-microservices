"""
User Account Service - FastAPI application.

This service handles user registration, authentication, and profile management.
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn

from database import get_db, engine, Base
from models import User
from schemas import (
    RegisterUserRequest,
    AuthorizeUserRequest,
    UpdateUserProfileRequest,
    BlockUserRequest,
    UserResponse,
    AuthResponse,
)
from auth import get_password_hash, verify_password, create_access_token
from datetime import timedelta


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    # Startup - create tables
    print("🚀 User Account service starting up...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # In test environment, database might already be set up
        print(f"Note: Database setup: {e}")
    yield
    # Shutdown
    print("🛑 User Account service shutting down...")


app = FastAPI(
    title="User Account Service",
    description="Service for managing user accounts, authentication, and profiles",
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
    "/api/v1/users/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
    summary="Register a new user",
)
async def register_user(request: RegisterUserRequest, db: Session = Depends(get_db)):
    """Register a new user in the system."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create new user
    hashed_password = get_password_hash(request.password)
    db_user = User(
        email=request.email,
        password_hash=hashed_password,
        first_name=request.first_name,
        last_name=request.last_name,
        phone=request.phone,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return UserResponse.model_validate(db_user)


@app.post(
    "/api/v1/users/authorize",
    response_model=AuthResponse,
    tags=["Users"],
    summary="Authorize user and get access token",
)
async def authorize_user(request: AuthorizeUserRequest, db: Session = Depends(get_db)):
    """Authorize user and return JWT token."""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Check if user is blocked
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is blocked"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.user_id})

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@app.get(
    "/api/v1/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Get user information",
)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user information by ID."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse.from_orm(user)


@app.put(
    "/api/v1/users/{user_id}/profile",
    response_model=UserResponse,
    tags=["Users"],
    summary="Update user profile",
)
async def update_user_profile(
    user_id: str, request: UpdateUserProfileRequest, db: Session = Depends(get_db)
):
    """Update user profile information."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update fields if provided
    if request.first_name is not None:
        user.first_name = request.first_name
    if request.last_name is not None:
        user.last_name = request.last_name
    if request.phone is not None:
        user.phone = request.phone

    db.commit()
    db.refresh(user)

    return UserResponse.from_orm(user)


@app.post(
    "/api/v1/users/{user_id}/block",
    response_model=UserResponse,
    tags=["Users"],
    summary="Block user account",
)
async def block_user(
    user_id: str, request: BlockUserRequest, db: Session = Depends(get_db)
):
    """Block a user account."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.is_blocked = True
    db.commit()
    db.refresh(user)

    return UserResponse.from_orm(user)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "user-account"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)

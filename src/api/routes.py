"""Additional API routes for authentication and user management."""

from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from src.api.auth import (
    authenticate_user, 
    create_access_token, 
    get_current_user,
    get_user,
    create_user,
    require_role,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.api.models import AuthToken, UserInfo
from src.utils.logger_service import get_logger

logger = get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """User registration request model."""
    username: str
    email: str
    password: str


@router.post("/auth/login", response_model=AuthToken, tags=["Authentication"])
async def login(request: LoginRequest):
    """Authenticate user and return access token."""
    try:
        user = authenticate_user(request.username, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, 
            expires_delta=access_token_expires
        )
        
        logger.info(f"User {request.username} logged in successfully")
        
        return AuthToken(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for {request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/auth/register", response_model=Dict[str, str], tags=["Authentication"])
async def register(request: RegisterRequest):
    """Register a new user account."""
    try:
        # Check if user already exists
        if get_user(request.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Create new user
        user = create_user(
            username=request.username,
            email=request.email,
            password=request.password,
            roles=["user"]
        )
        
        logger.info(f"New user registered: {request.username}")
        
        return {"message": "User registered successfully", "username": user["username"]}
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration failed for {request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.get("/auth/me", response_model=UserInfo, tags=["Authentication"])
async def get_current_user_info(current_user: str = Depends(get_current_user)):
    """Get current user information."""
    try:
        user = get_user(current_user)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserInfo(
            user_id=user["username"],  # Using username as ID for simplicity
            username=user["username"],
            email=user.get("email"),
            roles=user.get("roles", []),
            created_at=user["created_at"],
            last_login=user.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user info for {current_user}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.get("/auth/users", response_model=list[UserInfo], tags=["Administration"])
async def list_users(current_user: str = Depends(require_role("admin"))):
    """List all users (admin only)."""
    try:
        from src.api.auth import fake_users_db
        
        users = []
        for username, user_data in fake_users_db.items():
            users.append(UserInfo(
                user_id=username,
                username=username,
                email=user_data.get("email"),
                roles=user_data.get("roles", []),
                created_at=user_data["created_at"],
                last_login=user_data.get("last_login")
            ))
        
        return users
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )

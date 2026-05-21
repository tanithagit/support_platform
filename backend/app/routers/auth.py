from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.schemas.auth import (
    RegisterRequest, LoginRequest,
    TokenResponse, UserResponse
)
from app.services.auth_service import register_user, login_user
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, session: Session = Depends(get_session)):
    """Register a new user"""
    user = register_user(request, session)
    return user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, session: Session = Depends(get_session)):
    """Login and get JWT token"""
    token, user = login_user(request, session)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current logged in user info"""
    return current_user
from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from app.database import get_session
from app.schemas.user import UserResponse, UserUpdate, AgentCreate
from app.services.user_service import (
    get_user_by_id,
    get_agents_in_org,
    get_customers_in_org,
    create_agent,
    update_user,
    deactivate_user
)
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/agents", response_model=List[UserResponse])
def list_agents(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all agents in current user's organization"""
    return get_agents_in_org(current_user.organization_id, session)


@router.get("/customers", response_model=List[UserResponse])
def list_customers(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Get all customers — admin only"""
    return get_customers_in_org(current_user.organization_id, session)


@router.post("/agents", response_model=UserResponse)
def add_agent(
    request: AgentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Admin creates a new agent"""
    return create_agent(request, current_user.organization_id, session)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    return get_user_by_id(user_id, session)


@router.patch("/{user_id}", response_model=UserResponse)
def update(
    user_id: int,
    request: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update user details"""
    return update_user(user_id, request, current_user, session)


@router.delete("/{user_id}", response_model=UserResponse)
def deactivate(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Admin deactivates a user"""
    return deactivate_user(user_id, current_user, session)
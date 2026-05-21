from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserUpdate, AgentCreate
from app.core.security import hash_password


def get_user_by_id(user_id: int, session: Session):
    """Get user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def get_agents_in_org(org_id: int, session: Session):
    """Get all agents in an organization"""
    return session.exec(
        select(User).where(
            User.organization_id == org_id,
            User.role == "agent"
        )
    ).all()


def get_customers_in_org(org_id: int, session: Session):
    """Get all customers in an organization"""
    return session.exec(
        select(User).where(
            User.organization_id == org_id,
            User.role == "customer"
        )
    ).all()


def create_agent(
    request: AgentCreate,
    org_id: int,
    session: Session
):
    """Admin creates a new agent in their organization"""
    # Check email not taken
    existing = session.exec(
        select(User).where(User.email == request.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    agent = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        role="agent",
        organization_id=org_id
    )
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def update_user(
    user_id: int,
    request: UserUpdate,
    current_user: User,
    session: Session
):
    """Update user details"""
    user = get_user_by_id(user_id, session)

    # Only admin or the user themselves can update
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    # Only update fields that were provided
    if request.full_name is not None:
        user.full_name = request.full_name
    if request.is_active is not None:
        user.is_active = request.is_active

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def deactivate_user(
    user_id: int,
    current_user: User,
    session: Session
):
    """Admin deactivates a user"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    user = get_user_by_id(user_id, session)

    # Cannot deactivate yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )

    user.is_active = False
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
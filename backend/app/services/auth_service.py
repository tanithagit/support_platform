from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.user import User
from app.models.organization import Organization
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password, create_access_token
from datetime import timedelta
from app.config import settings


def register_user(request: RegisterRequest, session: Session):
    """Register a new user"""

    # Check if email already exists
    existing = session.exec(
        select(User).where(User.email == request.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate role
    valid_roles = ["admin", "agent", "customer"]
    if request.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role must be one of {valid_roles}"
        )

    # Handle organization
    org_id = request.organization_id

    if request.organization_name:
        # Create new organization
        org = Organization(name=request.organization_name)
        session.add(org)
        session.commit()
        session.refresh(org)
        org_id = org.id
    elif org_id:
        # Check organization exists
        org = session.get(Organization, org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

    # Create user
    user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        role=request.role,
        organization_id=org_id
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def login_user(request: LoginRequest, session: Session):
    """Login and return JWT token"""

    # Find user by email
    user = session.exec(
        select(User).where(User.email == request.email)
    ).first()

    # Verify user exists and password is correct
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Create JWT token
    token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "org_id": user.organization_id
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return token, user
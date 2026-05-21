from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from app.database import get_session
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.services.org_service import (
    get_organization,
    get_all_organizations,
    create_organization,
    get_org_members
)
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all organizations — any logged in user"""
    return get_all_organizations(session)


@router.post("/", response_model=OrganizationResponse)
def create_org(
    request: OrganizationCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    """Create organization — admin only"""
    return create_organization(request, session)


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_org(
    org_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get organization by ID"""
    # Non-admins can only see their own org
    if current_user.role != "admin":
        if current_user.organization_id != org_id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    return get_organization(org_id, session)


@router.get("/{org_id}/members", response_model=List[UserResponse])
def get_members(
    org_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all members of an organization"""
    if current_user.role != "admin":
        if current_user.organization_id != org_id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    return get_org_members(org_id, session)
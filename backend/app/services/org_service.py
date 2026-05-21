from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationCreate


def get_organization(org_id: int, session: Session):
    """Get organization by ID"""
    org = session.get(Organization, org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return org


def get_all_organizations(session: Session):
    """Get all organizations"""
    return session.exec(select(Organization)).all()


def create_organization(request: OrganizationCreate, session: Session):
    """Create a new organization"""
    # Check if name already exists
    existing = session.exec(
        select(Organization).where(Organization.name == request.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name already exists"
        )
    org = Organization(name=request.name)
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


def get_org_members(org_id: int, session: Session):
    """Get all users in an organization"""
    return session.exec(
        select(User).where(User.organization_id == org_id)
    ).all()
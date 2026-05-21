from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from app.database import get_session
from app.schemas.ticket import (
    TicketCreate, TicketUpdate, TicketAssign,
    TicketStatusUpdate, TicketResponse
)
from app.services.ticket_service import (
    create_ticket, get_tickets, get_ticket_by_id,
    assign_ticket, update_ticket_status,
    update_ticket, get_ticket_activity,
    get_dashboard_stats
)
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/", response_model=TicketResponse)
def create(
    request: TicketCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new ticket"""
    return create_ticket(request, current_user, session)


@router.get("/", response_model=List[TicketResponse])
def list_tickets(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get tickets based on role"""
    return get_tickets(current_user, session)


@router.get("/dashboard")
def dashboard(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""
    return get_dashboard_stats(current_user, session)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get single ticket by ID"""
    return get_ticket_by_id(ticket_id, current_user, session)


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update(
    ticket_id: int,
    request: TicketUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update ticket details"""
    return update_ticket(ticket_id, request, current_user, session)


@router.post("/{ticket_id}/assign", response_model=TicketResponse)
def assign(
    ticket_id: int,
    request: TicketAssign,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Admin assigns ticket to agent"""
    return assign_ticket(ticket_id, request, current_user, session)


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def change_status(
    ticket_id: int,
    request: TicketStatusUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update ticket status"""
    return update_ticket_status(
        ticket_id, request.status, current_user, session
    )


@router.get("/{ticket_id}/activity")
def get_activity(
    ticket_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get ticket activity log"""
    return get_ticket_activity(ticket_id, current_user, session)
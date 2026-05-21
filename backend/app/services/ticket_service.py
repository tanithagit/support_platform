from sqlmodel import Session, select
from fastapi import HTTPException, status
from datetime import datetime
from app.models.ticket import Ticket
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.models.message import Message
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketAssign


# ── Valid status transitions ─────────────────────────────
VALID_TRANSITIONS = {
    "open": ["in_progress"],
    "in_progress": ["resolved"],
    "resolved": ["closed"],
    "closed": []
}


def validate_status_transition(current: str, new: str):
    """Check if status change is allowed"""
    allowed = VALID_TRANSITIONS.get(current, [])
    if new not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from '{current}' to '{new}'. "
                   f"Allowed transitions: {allowed}"
        )


def log_activity(
    ticket_id: int,
    action: str,
    performed_by: int,
    session: Session
):
    """Record an activity in the log"""
    log = ActivityLog(
        ticket_id=ticket_id,
        action=action,
        performed_by=performed_by
    )
    session.add(log)


def send_auto_response(
    ticket_id: int,
    sender_id: int,
    message: str,
    session: Session
):
    """Send an automated message to the ticket"""
    auto_msg = Message(
        ticket_id=ticket_id,
        sender_id=sender_id,
        content=message,
        is_auto_response=True
    )
    session.add(auto_msg)


# ── Create Ticket ────────────────────────────────────────
def create_ticket(
    request: TicketCreate,
    current_user: User,
    session: Session
):
    """Customer creates a new ticket"""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must belong to an organization to create tickets"
        )

    # Validate priority
    valid_priorities = ["low", "medium", "high", "urgent"]
    if request.priority not in valid_priorities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Priority must be one of {valid_priorities}"
        )

    ticket = Ticket(
        subject=request.subject,
        description=request.description,
        priority=request.priority,
        status="open",
        organization_id=current_user.organization_id,
        customer_id=current_user.id
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    # Auto assign to available agent
    auto_assign_ticket(ticket, session)

    # Send auto response
    send_auto_response(
        ticket_id=ticket.id,
        sender_id=current_user.id,
        message=f"Thank you for contacting support! "
                f"Your ticket #{ticket.id} has been received. "
                f"We will get back to you shortly.",
        session=session
    )

    # Log activity
    log_activity(
        ticket_id=ticket.id,
        action=f"Ticket created by {current_user.full_name}",
        performed_by=current_user.id,
        session=session
    )

    session.commit()
    session.refresh(ticket)
    return ticket


# ── Auto Assign ──────────────────────────────────────────
def auto_assign_ticket(ticket: Ticket, session: Session):
    """Auto assign ticket to agent with least tickets"""
    agents = session.exec(
        select(User).where(
            User.organization_id == ticket.organization_id,
            User.role == "agent",
            User.is_active == True
        )
    ).all()

    if not agents:
        return

    # Find agent with fewest assigned open tickets
    agent_loads = {}
    for agent in agents:
        count = len(session.exec(
            select(Ticket).where(
                Ticket.assigned_to == agent.id,
                Ticket.status.in_(["open", "in_progress"])
            )
        ).all())
        agent_loads[agent.id] = count

    # Pick agent with minimum load
    best_agent_id = min(agent_loads, key=agent_loads.get)

    ticket.assigned_to = best_agent_id
    ticket.status = "in_progress"
    session.add(ticket)

    log_activity(
        ticket_id=ticket.id,
        action=f"Auto-assigned to agent ID {best_agent_id}",
        performed_by=ticket.customer_id,
        session=session
    )


# ── Get Tickets ──────────────────────────────────────────
def get_tickets(current_user: User, session: Session):
    """Get tickets based on user role"""
    if current_user.role == "customer":
        # Customers see only their own tickets
        tickets = session.exec(
            select(Ticket).where(
                Ticket.customer_id == current_user.id
            )
        ).all()

    elif current_user.role == "agent":
        # Agents see only assigned tickets
        tickets = session.exec(
            select(Ticket).where(
                Ticket.assigned_to == current_user.id
            )
        ).all()

    else:
        # Admin sees all tickets in their org
        tickets = session.exec(
            select(Ticket).where(
                Ticket.organization_id == current_user.organization_id
            )
        ).all()

    return tickets


def get_ticket_by_id(
    ticket_id: int,
    current_user: User,
    session: Session
):
    """Get a single ticket — with access control"""
    ticket = session.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Check org access
    if ticket.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Customer can only see their own ticket
    if current_user.role == "customer" and ticket.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Agent can only see assigned tickets
    if current_user.role == "agent" and ticket.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return ticket


# ── Assign Ticket ────────────────────────────────────────
def assign_ticket(
    ticket_id: int,
    request: TicketAssign,
    current_user: User,
    session: Session
):
    """Admin assigns ticket to an agent"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Verify agent exists and belongs to same org
    agent = session.get(User, request.agent_id)
    if not agent or agent.role != "agent":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid agent ID"
        )

    if agent.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent does not belong to your organization"
        )

    ticket.assigned_to = request.agent_id
    if ticket.status == "open":
        ticket.status = "in_progress"

    ticket.updated_at = datetime.utcnow()
    session.add(ticket)

    log_activity(
        ticket_id=ticket.id,
        action=f"Assigned to agent {agent.full_name} by {current_user.full_name}",
        performed_by=current_user.id,
        session=session
    )

    session.commit()
    session.refresh(ticket)
    return ticket


# ── Update Ticket Status ─────────────────────────────────
def update_ticket_status(
    ticket_id: int,
    new_status: str,
    current_user: User,
    session: Session
):
    """Update ticket status with transition validation"""
    ticket = get_ticket_by_id(ticket_id, current_user, session)

    # Validate transition
    validate_status_transition(ticket.status, new_status)

    old_status = ticket.status
    ticket.status = new_status
    ticket.updated_at = datetime.utcnow()

    if new_status == "resolved":
        ticket.resolved_at = datetime.utcnow()

    session.add(ticket)

    log_activity(
        ticket_id=ticket.id,
        action=f"Status changed from '{old_status}' to '{new_status}' "
               f"by {current_user.full_name}",
        performed_by=current_user.id,
        session=session
    )

    session.commit()
    session.refresh(ticket)
    return ticket


# ── Update Ticket Details ────────────────────────────────
def update_ticket(
    ticket_id: int,
    request: TicketUpdate,
    current_user: User,
    session: Session
):
    """Update ticket subject/description/priority"""
    ticket = get_ticket_by_id(ticket_id, current_user, session)

    if request.subject is not None:
        ticket.subject = request.subject
    if request.description is not None:
        ticket.description = request.description
    if request.priority is not None:
        valid_priorities = ["low", "medium", "high", "urgent"]
        if request.priority not in valid_priorities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Priority must be one of {valid_priorities}"
            )
        ticket.priority = request.priority

    ticket.updated_at = datetime.utcnow()
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return ticket


# ── Get Activity Log ─────────────────────────────────────
def get_ticket_activity(
    ticket_id: int,
    current_user: User,
    session: Session
):
    """Get activity log for a ticket"""
    ticket = get_ticket_by_id(ticket_id, current_user, session)
    logs = session.exec(
        select(ActivityLog).where(
            ActivityLog.ticket_id == ticket_id
        )
    ).all()
    return logs


# ── Dashboard Stats ──────────────────────────────────────
def get_dashboard_stats(current_user: User, session: Session):
    """Get stats for admin dashboard"""
    org_id = current_user.organization_id

    all_tickets = session.exec(
        select(Ticket).where(Ticket.organization_id == org_id)
    ).all()

    stats = {
        "total": len(all_tickets),
        "open": len([t for t in all_tickets if t.status == "open"]),
        "in_progress": len([t for t in all_tickets if t.status == "in_progress"]),
        "resolved": len([t for t in all_tickets if t.status == "resolved"]),
        "closed": len([t for t in all_tickets if t.status == "closed"]),
    }

    # Agent stats
    if current_user.role == "agent":
        my_tickets = [t for t in all_tickets if t.assigned_to == current_user.id]
        stats = {
            "total": len(my_tickets),
            "open": len([t for t in my_tickets if t.status == "open"]),
            "in_progress": len([t for t in my_tickets if t.status == "in_progress"]),
            "resolved": len([t for t in my_tickets if t.status == "resolved"]),
            "closed": len([t for t in my_tickets if t.status == "closed"]),
        }

    return stats
from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.message import Message
from app.models.ticket import Ticket
from app.models.user import User


def get_ticket_messages(
    ticket_id: int,
    current_user: User,
    session: Session
):
    """Get all messages for a ticket"""

    # Verify ticket exists
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Check access
    if ticket.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Customer can only see their own ticket messages
    if current_user.role == "customer":
        if ticket.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    # Agent can only see assigned ticket messages
    if current_user.role == "agent":
        if ticket.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    messages = session.exec(
        select(Message).where(
            Message.ticket_id == ticket_id
        ).order_by(Message.created_at)
    ).all()

    return messages


def save_message(
    ticket_id: int,
    sender_id: int,
    content: str,
    session: Session,
    is_auto_response: bool = False,
    file_url: str = None
):
    """Save a message to the database"""
    message = Message(
        ticket_id=ticket_id,
        sender_id=sender_id,
        content=content,
        is_auto_response=is_auto_response,
        file_url=file_url
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
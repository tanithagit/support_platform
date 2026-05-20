from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.models.enums import TicketStatus, TicketPriority

class Ticket(SQLModel, table=True):
    __tablename__ = "tickets"

    id: Optional[int] = Field(default=None, primary_key=True)
    subject: str
    description: str
    status: TicketStatus = Field(default=TicketStatus.open)
    priority: TicketPriority = Field(default=TicketPriority.medium)

    # Foreign Keys
    organization_id: int = Field(foreign_key="organizations.id")
    customer_id: int = Field(foreign_key="users.id")
    assigned_to: Optional[int] = Field(
        default=None, foreign_key="users.id"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(default=None)

    # Relationships
    organization: Optional["Organization"] = Relationship(
        back_populates="tickets"
    )
    customer: Optional["User"] = Relationship(
        back_populates="created_tickets",
        sa_relationship_kwargs={
            "foreign_keys": "[Ticket.customer_id]"
        }
    )
    assigned_agent: Optional["User"] = Relationship(
        back_populates="assigned_tickets",
        sa_relationship_kwargs={
            "foreign_keys": "[Ticket.assigned_to]"
        }
    )
    messages: List["Message"] = Relationship(back_populates="ticket")
    activity_logs: List["ActivityLog"] = Relationship(
        back_populates="ticket"
    )
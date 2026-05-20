from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.models.enums import UserRole

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    role: UserRole = Field(default=UserRole.customer)
    organization_id: Optional[int] = Field(
        default=None, foreign_key="organizations.id"
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    organization: Optional["Organization"] = Relationship(
        back_populates="users"
    )
    created_tickets: List["Ticket"] = Relationship(
        back_populates="customer",
        sa_relationship_kwargs={
            "foreign_keys": "[Ticket.customer_id]"
        }
    )
    assigned_tickets: List["Ticket"] = Relationship(
        back_populates="assigned_agent",
        sa_relationship_kwargs={
            "foreign_keys": "[Ticket.assigned_to]"
        }
    )
    messages: List["Message"] = Relationship(back_populates="sender")
    activity_logs: List["ActivityLog"] = Relationship(
        back_populates="performed_by_user"
    )
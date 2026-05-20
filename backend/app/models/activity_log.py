from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class ActivityLog(SQLModel, table=True):
    __tablename__ = "activity_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="tickets.id")
    action: str
    performed_by: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    ticket: Optional["Ticket"] = Relationship(
        back_populates="activity_logs"
    )
    performed_by_user: Optional["User"] = Relationship(
        back_populates="activity_logs"
    )
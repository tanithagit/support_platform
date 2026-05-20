from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="tickets.id")
    sender_id: int = Field(foreign_key="users.id")
    content: str
    is_auto_response: bool = Field(default=False)
    file_url: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    ticket: Optional["Ticket"] = Relationship(back_populates="messages")
    sender: Optional["User"] = Relationship(back_populates="messages")
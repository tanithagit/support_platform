from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Organization(SQLModel, table=True):
    __tablename__ = "organizations"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    users: List["User"] = Relationship(back_populates="organization")
    tickets: List["Ticket"] = Relationship(back_populates="organization")
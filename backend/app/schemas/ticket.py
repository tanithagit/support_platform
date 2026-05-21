from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TicketCreate(BaseModel):
    subject: str
    description: str
    priority: str = "medium"


class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None


class TicketAssign(BaseModel):
    agent_id: int


class TicketStatusUpdate(BaseModel):
    status: str


class TicketResponse(BaseModel):
    id: int
    subject: str
    description: str
    status: str
    priority: str
    organization_id: int
    customer_id: int
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TicketDetailResponse(TicketResponse):
    customer_name: Optional[str] = None
    agent_name: Optional[str] = None
    org_name: Optional[str] = None
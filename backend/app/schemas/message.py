from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageResponse(BaseModel):
    id: int
    ticket_id: int
    sender_id: int
    content: str
    is_auto_response: bool
    file_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str
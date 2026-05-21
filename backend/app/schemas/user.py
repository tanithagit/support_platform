from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    organization_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
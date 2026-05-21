from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ── Request Schemas (what frontend sends) ──────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "customer"
    organization_id: Optional[int] = None
    organization_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ── Response Schemas (what backend sends back) ──────────

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    organization_id: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
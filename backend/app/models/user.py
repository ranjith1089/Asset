from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class User(BaseModel):
    """User model for authentication with tenant support"""
    id: UUID
    email: Optional[str] = None
    tenant_id: Optional[UUID] = None
    role: Optional[str] = None
    status: Optional[str] = None
    
    class Config:
        from_attributes = True


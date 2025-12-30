from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class AuditLogBase(BaseModel):
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    tenant_id: Optional[UUID] = None
    user_id: UUID


class AuditLog(AuditLogBase):
    id: UUID
    tenant_id: Optional[UUID] = None
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogQuery(BaseModel):
    tenant_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 100


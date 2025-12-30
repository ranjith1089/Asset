from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class TenantBase(BaseModel):
    name: str = Field(..., description="Company/Organization name")
    slug: Optional[str] = Field(None, description="URL-friendly identifier")
    logo_url: Optional[str] = None
    theme: Optional[Dict[str, Any]] = Field(default_factory=dict)
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TenantCreate(TenantBase):
    slug: str = Field(..., description="URL-friendly identifier (auto-generated if not provided)")


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    theme: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(active|suspended|deleted)$")


class Tenant(TenantBase):
    id: UUID
    status: str
    subscription_plan: str
    subscription_status: str
    subscription_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


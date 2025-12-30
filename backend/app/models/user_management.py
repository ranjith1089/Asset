from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    name: str
    email: EmailStr
    mobile: Optional[str] = None
    role: str = Field(default="staff", pattern="^(super_admin|tenant_admin|manager|staff|viewer)$")
    status: str = Field(default="active", pattern="^(active|inactive|suspended)$")


class UserCreate(UserBase):
    tenant_id: UUID
    password: Optional[str] = None  # For creating users with password


class UserUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(super_admin|tenant_admin|manager|staff|viewer)$")
    status: Optional[str] = Field(None, pattern="^(active|inactive|suspended)$")


class User(UserBase):
    id: UUID
    tenant_id: UUID
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserWithTenant(User):
    tenant_name: Optional[str] = None


from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID


class RoleBase(BaseModel):
    name: str
    permissions: Dict[str, Any] = Field(default_factory=dict, description="Permission matrix as JSON")
    is_system_role: bool = False


class RoleCreate(RoleBase):
    tenant_id: UUID


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None


class Role(RoleBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    resource: str
    action: str
    description: Optional[str] = None


class Permission(PermissionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


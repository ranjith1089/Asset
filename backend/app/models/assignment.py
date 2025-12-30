from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class AssignmentBase(BaseModel):
    asset_id: UUID
    employee_id: UUID
    assigned_date: date
    notes: Optional[str] = None


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentReturn(BaseModel):
    returned_date: Optional[date] = None
    notes: Optional[str] = None


class Assignment(AssignmentBase):
    id: UUID
    tenant_id: UUID
    assigned_by: UUID
    returned_date: Optional[date] = None
    status: str  # active, returned
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class AssignmentWithDetails(Assignment):
    asset_name: Optional[str] = None
    asset_tag: Optional[str] = None
    employee_name: Optional[str] = None


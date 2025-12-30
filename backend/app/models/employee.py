from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    department: Optional[str] = None
    position: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    position: Optional[str] = None


class Employee(EmployeeBase):
    id: UUID
    tenant_id: UUID
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


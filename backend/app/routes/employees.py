from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from app.database import supabase
from app.models.employee import Employee, EmployeeCreate, EmployeeUpdate
from app.dependencies import get_user, get_tenant
from app.models.user import User
from app.utils.permissions import Resource, Action, has_permission

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=List[Employee])
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    department: str = None,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """Get all employees with optional filtering (tenant-scoped)"""
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.EMPLOYEES, Action.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = supabase.table("employees").select("*").eq("tenant_id", str(tenant_id))
    
    if department:
        query = query.eq("department", department)
    
    query = query.order("created_at", desc=True).range(skip, skip + limit - 1)
    response = query.execute()
    
    return response.data


@router.get("/{employee_id}", response_model=Employee)
async def get_employee(
    employee_id: UUID,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """Get a specific employee by ID (tenant-scoped)"""
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.EMPLOYEES, Action.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    response = supabase.table("employees").select("*").eq("id", str(employee_id)).eq("tenant_id", str(tenant_id)).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return response.data[0]


@router.post("", response_model=Employee, status_code=201)
async def create_employee(
    employee: EmployeeCreate,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """Create a new employee (tenant-scoped)"""
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.EMPLOYEES, Action.CREATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if email already exists in this tenant
    existing = supabase.table("employees").select("id").eq("email", employee.email).eq("tenant_id", str(tenant_id)).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Employee with this email already exists")
    
    employee_dict = employee.model_dump()
    employee_dict["tenant_id"] = str(tenant_id)  # Auto-inject tenant_id
    response = supabase.table("employees").insert(employee_dict).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create employee")
    
    return response.data[0]


@router.put("/{employee_id}", response_model=Employee)
async def update_employee(
    employee_id: UUID,
    employee_update: EmployeeUpdate,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """Update an existing employee (tenant-scoped)"""
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.EMPLOYEES, Action.UPDATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if employee exists and belongs to tenant
    existing = supabase.table("employees").select("*").eq("id", str(employee_id)).eq("tenant_id", str(tenant_id)).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if email is being updated and if it already exists in this tenant
    update_dict = employee_update.model_dump(exclude_unset=True)
    if "email" in update_dict:
        email_check = supabase.table("employees").select("id").eq("email", update_dict["email"]).eq("tenant_id", str(tenant_id)).neq("id", str(employee_id)).execute()
        if email_check.data:
            raise HTTPException(status_code=400, detail="Employee with this email already exists")
    
    response = supabase.table("employees").update(update_dict).eq("id", str(employee_id)).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to update employee")
    
    return response.data[0]


@router.delete("/{employee_id}", status_code=204)
async def delete_employee(
    employee_id: UUID,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """Delete an employee (tenant-scoped)"""
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.EMPLOYEES, Action.DELETE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Verify employee belongs to tenant
    employee_check = supabase.table("employees").select("id").eq("id", str(employee_id)).eq("tenant_id", str(tenant_id)).execute()
    if not employee_check.data:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if employee has active assignments
    active_assignments = supabase.table("assignments").select("id").eq("employee_id", str(employee_id)).eq("status", "active").execute()
    if active_assignments.data:
        raise HTTPException(status_code=400, detail="Cannot delete employee with active assignments")
    
    response = supabase.table("employees").delete().eq("id", str(employee_id)).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return None


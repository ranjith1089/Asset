from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from app.database import supabase
from app.models.employee import Employee, EmployeeCreate, EmployeeUpdate
from app.dependencies import get_user
from app.models.user import User

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=List[Employee])
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    department: str = None,
    current_user: User = Depends(get_user)
):
    """Get all employees with optional filtering"""
    query = supabase.table("employees").select("*")
    
    if department:
        query = query.eq("department", department)
    
    query = query.order("created_at", desc=True).range(skip, skip + limit - 1)
    response = query.execute()
    
    return response.data


@router.get("/{employee_id}", response_model=Employee)
async def get_employee(employee_id: UUID, current_user: User = Depends(get_user)):
    """Get a specific employee by ID"""
    response = supabase.table("employees").select("*").eq("id", str(employee_id)).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return response.data[0]


@router.post("", response_model=Employee, status_code=201)
async def create_employee(employee: EmployeeCreate, current_user: User = Depends(get_user)):
    """Create a new employee"""
    # Check if email already exists
    existing = supabase.table("employees").select("id").eq("email", employee.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Employee with this email already exists")
    
    employee_dict = employee.model_dump()
    response = supabase.table("employees").insert(employee_dict).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create employee")
    
    return response.data[0]


@router.put("/{employee_id}", response_model=Employee)
async def update_employee(
    employee_id: UUID,
    employee_update: EmployeeUpdate,
    current_user: User = Depends(get_user)
):
    """Update an existing employee"""
    # Check if employee exists
    existing = supabase.table("employees").select("*").eq("id", str(employee_id)).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if email is being updated and if it already exists
    update_dict = employee_update.model_dump(exclude_unset=True)
    if "email" in update_dict:
        email_check = supabase.table("employees").select("id").eq("email", update_dict["email"]).neq("id", str(employee_id)).execute()
        if email_check.data:
            raise HTTPException(status_code=400, detail="Employee with this email already exists")
    
    response = supabase.table("employees").update(update_dict).eq("id", str(employee_id)).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to update employee")
    
    return response.data[0]


@router.delete("/{employee_id}", status_code=204)
async def delete_employee(employee_id: UUID, current_user: User = Depends(get_user)):
    """Delete an employee"""
    # Check if employee has active assignments
    active_assignments = supabase.table("assignments").select("id").eq("employee_id", str(employee_id)).eq("status", "active").execute()
    if active_assignments.data:
        raise HTTPException(status_code=400, detail="Cannot delete employee with active assignments")
    
    response = supabase.table("employees").delete().eq("id", str(employee_id)).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return None


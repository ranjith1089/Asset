from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from datetime import date
from app.database import supabase
from app.models.assignment import Assignment, AssignmentCreate, AssignmentReturn, AssignmentWithDetails
from app.dependencies import get_user, get_tenant
from app.models.user import User
from app.utils.permissions import Resource, Action, has_permission

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("", response_model=List[AssignmentWithDetails])
async def get_assignments(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    asset_id: UUID = None,
    employee_id: UUID = None,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """Get all assignments with optional filtering (tenant-scoped)"""
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.ASSIGNMENTS, Action.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = supabase.table("assignments").select(
        "*, assets(name, asset_tag), employees(name)"
    ).eq("tenant_id", str(tenant_id))
    
    if status:
        query = query.eq("status", status)
    if asset_id:
        query = query.eq("asset_id", str(asset_id))
    if employee_id:
        query = query.eq("employee_id", str(employee_id))
    
    query = query.order("created_at", desc=True).range(skip, skip + limit - 1)
    response = query.execute()
    
    # Transform the response to match AssignmentWithDetails model
    assignments = []
    for item in response.data:
        assignment = item.copy()
        if item.get("assets"):
            assignment["asset_name"] = item["assets"].get("name")
            assignment["asset_tag"] = item["assets"].get("asset_tag")
        if item.get("employees"):
            assignment["employee_name"] = item["employees"].get("name")
        # Remove nested objects
        assignment.pop("assets", None)
        assignment.pop("employees", None)
        assignments.append(assignment)
    
    return assignments


@router.get("/{assignment_id}", response_model=AssignmentWithDetails)
async def get_assignment(
    assignment_id: UUID,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """Get a specific assignment by ID (tenant-scoped)"""
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.ASSIGNMENTS, Action.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    response = supabase.table("assignments").select(
        "*, assets(name, asset_tag), employees(name)"
    ).eq("id", str(assignment_id)).eq("tenant_id", str(tenant_id)).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    item = response.data[0]
    assignment = item.copy()
    if item.get("assets"):
        assignment["asset_name"] = item["assets"].get("name")
        assignment["asset_tag"] = item["assets"].get("asset_tag")
    if item.get("employees"):
        assignment["employee_name"] = item["employees"].get("name")
    assignment.pop("assets", None)
    assignment.pop("employees", None)
    
    return assignment


@router.post("", response_model=Assignment, status_code=201)
async def create_assignment(
    assignment: AssignmentCreate,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """Assign an asset to an employee (tenant-scoped)"""
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.ASSIGNMENTS, Action.CREATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Check if asset exists and belongs to tenant
    asset_response = supabase.table("assets").select("*").eq("id", str(assignment.asset_id)).eq("tenant_id", str(tenant_id)).execute()
    if not asset_response.data:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset = asset_response.data[0]
    if asset["status"] not in ["available", "assigned"]:
        raise HTTPException(status_code=400, detail=f"Cannot assign asset with status: {asset['status']}")
    
    # Check if employee exists and belongs to tenant
    employee_response = supabase.table("employees").select("id").eq("id", str(assignment.employee_id)).eq("tenant_id", str(tenant_id)).execute()
    if not employee_response.data:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check for active assignments for this asset
    active_assignments = supabase.table("assignments").select("id").eq("asset_id", str(assignment.asset_id)).eq("status", "active").execute()
    if active_assignments.data:
        raise HTTPException(status_code=400, detail="Asset already has an active assignment")
    
    assignment_dict = assignment.model_dump()
    assignment_dict["assigned_by"] = str(current_user.id)
    assignment_dict["tenant_id"] = str(tenant_id)  # Auto-inject tenant_id
    assignment_dict["status"] = "active"
    
    # Convert UUIDs to strings for Supabase
    assignment_dict["asset_id"] = str(assignment_dict["asset_id"])
    assignment_dict["employee_id"] = str(assignment_dict["employee_id"])
    
    # Convert date to string for Supabase
    if assignment_dict.get("assigned_date") and hasattr(assignment_dict["assigned_date"], "isoformat"):
        assignment_dict["assigned_date"] = assignment_dict["assigned_date"].isoformat()
    
    try:
        # Create assignment
        response = supabase.table("assignments").insert(assignment_dict).execute()
        
        # Check for errors in the response
        if hasattr(response, 'error') and response.error:
            error_msg = str(response.error)
            raise HTTPException(status_code=400, detail=f"Failed to create assignment: {error_msg}")
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create assignment - no data returned")
        
        # Update asset status
        supabase.table("assets").update({"status": "assigned"}).eq("id", str(assignment.asset_id)).execute()
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(status_code=400, detail=f"Failed to create assignment: {error_msg}")


@router.put("/{assignment_id}/return", response_model=Assignment)
async def return_assignment(
    assignment_id: UUID,
    return_data: AssignmentReturn,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """Return an assigned asset (tenant-scoped)"""
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.ASSIGNMENTS, Action.UPDATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Get assignment and verify it belongs to tenant
    assignment_response = supabase.table("assignments").select("*").eq("id", str(assignment_id)).eq("tenant_id", str(tenant_id)).execute()
    if not assignment_response.data:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    assignment = assignment_response.data[0]
    if assignment["status"] != "active":
        raise HTTPException(status_code=400, detail="Assignment is not active")
    
    # Update assignment
    return_date = return_data.returned_date or date.today()
    update_dict = {
        "status": "returned",
        "returned_date": return_date.isoformat()
    }
    if return_data.notes:
        update_dict["notes"] = return_data.notes
    
    response = supabase.table("assignments").update(update_dict).eq("id", str(assignment_id)).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to return assignment")
    
    # Update asset status to available
    supabase.table("assets").update({"status": "available"}).eq("id", assignment["asset_id"]).execute()
    
    return response.data[0]


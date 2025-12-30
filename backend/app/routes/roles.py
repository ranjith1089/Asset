from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from app.models.role import Role, RoleCreate, RoleUpdate
from app.dependencies import get_user, get_tenant
from app.models.user import User
from app.database import supabase
from app.utils.permissions import Resource, Action, has_permission

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=List[Role])
async def list_roles(
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """
    List roles in tenant
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.ROLES, Action.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        response = supabase.table("roles").select("*").eq("tenant_id", str(tenant_id)).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch roles: {str(e)}")


@router.get("/{role_id}", response_model=Role)
async def get_role(
    role_id: UUID,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """
    Get role by ID
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.ROLES, Action.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        response = supabase.table("roles").select("*").eq("id", str(role_id)).eq("tenant_id", str(tenant_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Role not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch role: {str(e)}")


@router.post("", response_model=Role)
async def create_role(
    role: RoleCreate,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """
    Create custom role (tenant_admin)
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.ROLES, Action.CREATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Ensure role is created in current tenant
    role.tenant_id = tenant_id
    
    try:
        role_data = role.model_dump(exclude_unset=True)
        response = supabase.table("roles").insert(role_data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create role")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create role: {str(e)}")


@router.put("/{role_id}", response_model=Role)
async def update_role(
    role_id: UUID,
    role_update: RoleUpdate,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """
    Update role (tenant_admin)
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.ROLES, Action.UPDATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Verify role exists and belongs to tenant
        role_response = supabase.table("roles").select("tenant_id, is_system_role").eq("id", str(role_id)).execute()
        if not role_response.data:
            raise HTTPException(status_code=404, detail="Role not found")
        
        if UUID(role_response.data[0]["tenant_id"]) != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Prevent updating system roles (optional - can be removed if you want to allow it)
        if role_response.data[0].get("is_system_role") and current_user.role != "super_admin":
            raise HTTPException(status_code=403, detail="Cannot update system roles")
        
        update_data = role_update.model_dump(exclude_unset=True)
        response = supabase.table("roles").update(update_data).eq("id", str(role_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Role not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update role: {str(e)}")


@router.delete("/{role_id}")
async def delete_role(
    role_id: UUID,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """
    Delete role (tenant_admin)
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.ROLES, Action.DELETE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Verify role exists and belongs to tenant
        role_response = supabase.table("roles").select("tenant_id, is_system_role").eq("id", str(role_id)).execute()
        if not role_response.data:
            raise HTTPException(status_code=404, detail="Role not found")
        
        if UUID(role_response.data[0]["tenant_id"]) != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Prevent deleting system roles
        if role_response.data[0].get("is_system_role"):
            raise HTTPException(status_code=403, detail="Cannot delete system roles")
        
        response = supabase.table("roles").delete().eq("id", str(role_id)).execute()
        return {"message": "Role deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete role: {str(e)}")


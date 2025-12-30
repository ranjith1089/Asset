from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from app.models.tenant import Tenant, TenantCreate, TenantUpdate
from app.dependencies import get_user
from app.models.user import User
from app.database import supabase
from app.utils.permissions import Resource, Action, has_permission

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("", response_model=List[Tenant])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_user)
):
    """
    List all tenants (super_admin only)
    """
    if not current_user.role or current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admins can list all tenants")
    
    try:
        response = supabase.table("tenants").select("*").range(skip, skip + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tenants: {str(e)}")


@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(
    tenant_id: UUID,
    current_user: User = Depends(get_user)
):
    """
    Get tenant details
    """
    # Super admin can view any tenant, others can only view their own
    if current_user.role != "super_admin":
        if not current_user.tenant_id or current_user.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        response = supabase.table("tenants").select("*").eq("id", str(tenant_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tenant: {str(e)}")


@router.post("", response_model=Tenant)
async def create_tenant(
    tenant: TenantCreate,
    current_user: User = Depends(get_user)
):
    """
    Create new tenant (super_admin only)
    """
    if not current_user.role or current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admins can create tenants")
    
    try:
        tenant_data = tenant.model_dump(exclude_unset=True)
        response = supabase.table("tenants").insert(tenant_data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create tenant")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")


@router.put("/{tenant_id}", response_model=Tenant)
async def update_tenant(
    tenant_id: UUID,
    tenant_update: TenantUpdate,
    current_user: User = Depends(get_user)
):
    """
    Update tenant
    """
    # Super admin can update any tenant, tenant admin can update their own
    if current_user.role != "super_admin":
        if not current_user.tenant_id or current_user.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        if current_user.role != "tenant_admin":
            raise HTTPException(status_code=403, detail="Only tenant admins can update tenant settings")
    
    try:
        update_data = tenant_update.model_dump(exclude_unset=True)
        response = supabase.table("tenants").update(update_data).eq("id", str(tenant_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update tenant: {str(e)}")


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: UUID,
    current_user: User = Depends(get_user)
):
    """
    Suspend or delete tenant (super_admin only)
    """
    if not current_user.role or current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admins can delete tenants")
    
    try:
        # Soft delete - update status to deleted
        response = supabase.table("tenants").update({"status": "deleted"}).eq("id", str(tenant_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return {"message": "Tenant deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete tenant: {str(e)}")


@router.get("/current/info", response_model=Tenant)
async def get_current_tenant_info(current_user: User = Depends(get_user)):
    """
    Get current user's tenant information
    """
    if not current_user.tenant_id:
        raise HTTPException(status_code=404, detail="User is not associated with a tenant")
    
    try:
        response = supabase.table("tenants").select("*").eq("id", str(current_user.tenant_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tenant: {str(e)}")


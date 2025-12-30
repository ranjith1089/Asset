from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from app.models.user_management import User, UserCreate, UserUpdate
from app.dependencies import get_user, get_tenant
from app.models.user import User as AuthUser
from app.database import supabase
from app.utils.permissions import Resource, Action, has_permission

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    tenant_id: UUID = Depends(get_tenant),
    current_user: AuthUser = Depends(get_user)
):
    """
    List users in tenant (RBAC controlled)
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.USERS, Action.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Super admin can view all users, others only their tenant
        if current_user.role == "super_admin":
            response = supabase.table("users").select("*").range(skip, skip + limit - 1).execute()
        else:
            response = supabase.table("users").select("*").eq("tenant_id", str(tenant_id)).range(skip, skip + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: UUID,
    tenant_id: UUID = Depends(get_tenant),
    current_user: AuthUser = Depends(get_user)
):
    """
    Get user by ID
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.USERS, Action.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        response = supabase.table("users").select("*").eq("id", str(user_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = response.data[0]
        # Check tenant access (super admin can access any, others only their tenant)
        if current_user.role != "super_admin":
            if UUID(user_data["tenant_id"]) != tenant_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")


@router.post("", response_model=User)
async def create_user(
    user: UserCreate,
    tenant_id: UUID = Depends(get_tenant),
    current_user: AuthUser = Depends(get_user)
):
    """
    Create new user (tenant_admin+)
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.USERS, Action.CREATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Ensure user is created in current tenant (unless super admin)
    if current_user.role != "super_admin":
        user.tenant_id = tenant_id
    
    try:
        user_data = user.model_dump(exclude_unset=True, exclude={"password"})
        
        # Create Supabase auth user if password provided
        if user.password:
            auth_response = supabase.auth.sign_up({
                "email": user.email,
                "password": user.password,
                "options": {
                    "data": {
                        "name": user.name
                    }
                }
            })
            if not auth_response.user:
                raise HTTPException(status_code=400, detail="Failed to create auth user")
            user_data["id"] = auth_response.user.id
        else:
            # Generate UUID for user (will need to be linked to auth user later)
            from uuid import uuid4
            user_data["id"] = str(uuid4())
        
        response = supabase.table("users").insert(user_data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    tenant_id: UUID = Depends(get_tenant),
    current_user: AuthUser = Depends(get_user)
):
    """
    Update user (tenant_admin+)
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.USERS, Action.UPDATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Verify user exists and belongs to tenant (unless super admin)
        user_response = supabase.table("users").select("tenant_id").eq("id", str(user_id)).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        if current_user.role != "super_admin":
            if UUID(user_response.data[0]["tenant_id"]) != tenant_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        update_data = user_update.model_dump(exclude_unset=True)
        response = supabase.table("users").update(update_data).eq("id", str(user_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    tenant_id: UUID = Depends(get_tenant),
    current_user: AuthUser = Depends(get_user)
):
    """
    Deactivate user (tenant_admin+)
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.USERS, Action.DELETE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Verify user exists and belongs to tenant (unless super admin)
        user_response = supabase.table("users").select("tenant_id").eq("id", str(user_id)).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        if current_user.role != "super_admin":
            if UUID(user_response.data[0]["tenant_id"]) != tenant_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Soft delete - update status to inactive
        response = supabase.table("users").update({"status": "inactive"}).eq("id", str(user_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


@router.post("/{user_id}/change-role")
async def change_user_role(
    user_id: UUID,
    new_role: str,
    tenant_id: UUID = Depends(get_tenant),
    current_user: AuthUser = Depends(get_user)
):
    """
    Change user role (tenant_admin+)
    Accepts new_role as query parameter
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.USERS, Action.UPDATE):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Validate role
    valid_roles = ["super_admin", "tenant_admin", "manager", "staff", "viewer"]
    if new_role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}")
    
    # Prevent non-super-admins from creating super admins
    if new_role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admins can assign super_admin role")
    
    try:
        # Verify user exists and belongs to tenant (unless super admin)
        user_response = supabase.table("users").select("tenant_id").eq("id", str(user_id)).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        if current_user.role != "super_admin":
            if UUID(user_response.data[0]["tenant_id"]) != tenant_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        response = supabase.table("users").update({"role": new_role}).eq("id", str(user_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User role updated successfully", "user": response.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")


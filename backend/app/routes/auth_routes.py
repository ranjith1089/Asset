from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import supabase
from app.models.tenant import TenantCreate
from app.models.user_management import UserCreate
from app.utils.auth import get_current_user
from app.models.user import User
from uuid import uuid4
import re

router = APIRouter(prefix="/auth", tags=["authentication"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    organization_name: str
    organization_slug: Optional[str] = None


class SignupResponse(BaseModel):
    user_id: str
    tenant_id: str
    email: str
    message: str


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from organization name"""
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower())
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug[:50]  # Limit length


@router.post("/signup", response_model=SignupResponse)
async def signup(request: SignupRequest):
    """
    Public signup endpoint - creates tenant and user
    """
    try:
        # Generate slug if not provided
        slug = request.organization_slug or generate_slug(request.organization_name)
        
        # Check if slug already exists
        existing_tenant = supabase.table("tenants").select("id").eq("slug", slug).execute()
        if existing_tenant.data:
            # Append random suffix if slug exists
            slug = f"{slug}-{uuid4().hex[:8]}"
        
        # Create Supabase auth user
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "name": request.name,
                    "organization_name": request.organization_name
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Failed to create user")
        
        user_id = auth_response.user.id
        
        # Create tenant
        tenant_data = {
            "name": request.organization_name,
            "slug": slug,
            "status": "active",
            "subscription_plan": "trial",
            "subscription_status": "active"
        }
        tenant_response = supabase.table("tenants").insert(tenant_data).execute()
        
        if not tenant_response.data:
            # Rollback: delete auth user if tenant creation fails
            # Note: Admin API might not be available, so we'll just raise the error
            raise HTTPException(status_code=500, detail="Failed to create tenant")
        
        tenant_id = tenant_response.data[0]["id"]
        
        # Create user record
        user_data = {
            "id": user_id,
            "tenant_id": tenant_id,
            "name": request.name,
            "email": request.email,
            "role": "tenant_admin",
            "status": "active"
        }
        user_response = supabase.table("users").insert(user_data).execute()
        
        if not user_response.data:
            # Rollback: delete tenant if user creation fails
            try:
                supabase.table("tenants").delete().eq("id", tenant_id).execute()
            except:
                pass
            raise HTTPException(status_code=500, detail="Failed to create user record")
        
        # Create default subscription
        from datetime import datetime, timedelta
        subscription_data = {
            "tenant_id": tenant_id,
            "plan": "trial",
            "status": "active",
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=14)).isoformat()
        }
        try:
            supabase.table("subscriptions").insert(subscription_data).execute()
        except:
            # Subscription creation is not critical
            pass
        
        # Create default roles for tenant
        default_roles = [
            {
                "tenant_id": tenant_id,
                "name": "Tenant Admin",
                "permissions": {
                    "assets": ["create", "read", "update", "delete", "manage"],
                    "employees": ["create", "read", "update", "delete", "manage"],
                    "assignments": ["create", "read", "update", "delete", "manage"],
                    "users": ["create", "read", "update", "delete", "manage"],
                    "roles": ["create", "read", "update", "delete"],
                    "settings": ["read", "update"],
                    "audit_logs": ["read"]
                },
                "is_system_role": True
            },
            {
                "tenant_id": tenant_id,
                "name": "Manager",
                "permissions": {
                    "assets": ["create", "read", "update", "delete"],
                    "employees": ["create", "read", "update"],
                    "assignments": ["create", "read", "update", "delete"],
                    "users": ["read"],
                    "roles": ["read"],
                    "settings": ["read"],
                    "audit_logs": ["read"]
                },
                "is_system_role": True
            },
            {
                "tenant_id": tenant_id,
                "name": "Staff",
                "permissions": {
                    "assets": ["read", "update"],
                    "employees": ["read"],
                    "assignments": ["create", "read", "update"],
                    "users": ["read"],
                    "roles": ["read"],
                    "settings": ["read"]
                },
                "is_system_role": True
            },
            {
                "tenant_id": tenant_id,
                "name": "Viewer",
                "permissions": {
                    "assets": ["read"],
                    "employees": ["read"],
                    "assignments": ["read"],
                    "users": ["read"],
                    "roles": ["read"],
                    "settings": ["read"]
                },
                "is_system_role": True
            }
        ]
        try:
            supabase.table("roles").insert(default_roles).execute()
        except:
            # Role creation is not critical for signup
            pass
        
        return SignupResponse(
            user_id=user_id,
            tenant_id=tenant_id,
            email=request.email,
            message="Signup successful! Please check your email to verify your account."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "tenant_id": str(current_user.tenant_id) if current_user.tenant_id else None,
        "role": current_user.role,
        "status": current_user.status
    }


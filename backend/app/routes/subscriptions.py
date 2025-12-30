from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from datetime import datetime, timedelta
from app.models.subscription import Subscription, SubscriptionUpdate, Invoice
from app.dependencies import get_user, get_tenant
from app.models.user import User
from app.database import supabase

router = APIRouter(prefix="/subscription", tags=["subscriptions"])


@router.get("", response_model=Subscription)
async def get_current_subscription(
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """
    Get current subscription for tenant
    """
    try:
        response = supabase.table("subscriptions").select("*").eq("tenant_id", str(tenant_id)).execute()
        if not response.data:
            # Create default free subscription if none exists
            subscription_data = {
                "tenant_id": str(tenant_id),
                "plan": "free",
                "status": "active",
                "current_period_start": datetime.utcnow().isoformat(),
                "current_period_end": (datetime.utcnow() + timedelta(days=365)).isoformat()
            }
            create_response = supabase.table("subscriptions").insert(subscription_data).execute()
            return create_response.data[0]
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch subscription: {str(e)}")


@router.post("/upgrade")
async def upgrade_subscription(
    plan: str,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """
    Upgrade subscription plan (tenant_admin only)
    """
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Only tenant admins can upgrade subscription")
    
    valid_plans = ["free", "trial", "basic", "premium", "enterprise"]
    if plan not in valid_plans:
        raise HTTPException(status_code=400, detail=f"Invalid plan. Must be one of: {', '.join(valid_plans)}")
    
    try:
        # Get current subscription
        sub_response = supabase.table("subscriptions").select("*").eq("tenant_id", str(tenant_id)).execute()
        
        update_data = {
            "plan": plan,
            "status": "active",
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "cancel_at_period_end": False
        }
        
        if sub_response.data:
            # Update existing subscription
            response = supabase.table("subscriptions").update(update_data).eq("tenant_id", str(tenant_id)).execute()
        else:
            # Create new subscription
            update_data["tenant_id"] = str(tenant_id)
            response = supabase.table("subscriptions").insert(update_data).execute()
        
        # Update tenant subscription info
        supabase.table("tenants").update({
            "subscription_plan": plan,
            "subscription_status": "active"
        }).eq("id", str(tenant_id)).execute()
        
        return {"message": "Subscription upgraded successfully", "subscription": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upgrade subscription: {str(e)}")


@router.post("/cancel")
async def cancel_subscription(
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """
    Cancel subscription (tenant_admin only)
    """
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Only tenant admins can cancel subscription")
    
    try:
        update_data = {
            "cancel_at_period_end": True,
            "status": "active"  # Keep active until period ends
        }
        response = supabase.table("subscriptions").update(update_data).eq("tenant_id", str(tenant_id)).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        return {"message": "Subscription will be cancelled at the end of the current period"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")


@router.get("/invoices", response_model=List[Invoice])
async def list_invoices(
    skip: int = 0,
    limit: int = 100,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """
    List invoices for tenant (tenant_admin+)
    """
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        response = supabase.table("invoices").select("*").eq("tenant_id", str(tenant_id)).order("created_at", desc=True).range(skip, skip + limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch invoices: {str(e)}")


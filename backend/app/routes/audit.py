from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.models.audit import AuditLog, AuditLogQuery
from app.dependencies import get_user, get_tenant
from app.models.user import User
from app.database import supabase
from app.utils.permissions import Resource, Action, has_permission

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=List[AuditLog])
async def get_audit_logs(
    query: AuditLogQuery = Depends(),
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """
    Query audit logs (tenant_admin+)
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.AUDIT_LOGS, Action.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Build query
        db_query = supabase.table("audit_logs").select("*")
        
        # Super admin can see all logs, others only their tenant
        if current_user.role != "super_admin":
            db_query = db_query.eq("tenant_id", str(tenant_id))
        elif query.tenant_id:
            db_query = db_query.eq("tenant_id", str(query.tenant_id))
        
        if query.user_id:
            db_query = db_query.eq("user_id", str(query.user_id))
        
        if query.action:
            db_query = db_query.eq("action", query.action)
        
        if query.resource_type:
            db_query = db_query.eq("resource_type", query.resource_type)
        
        if query.start_date:
            db_query = db_query.gte("created_at", query.start_date.isoformat())
        
        if query.end_date:
            db_query = db_query.lte("created_at", query.end_date.isoformat())
        
        # Order by created_at descending and apply pagination
        response = db_query.order("created_at", desc=True).range(query.skip, query.skip + query.limit - 1).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit logs: {str(e)}")


@router.get("/{log_id}", response_model=AuditLog)
async def get_audit_log(
    log_id: UUID,
    tenant_id: UUID = Depends(get_tenant),
    current_user: User = Depends(get_user)
):
    """
    Get specific audit log entry
    """
    # Check permission
    if not has_permission(current_user.role or "viewer", Resource.AUDIT_LOGS, Action.READ):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        response = supabase.table("audit_logs").select("*").eq("id", str(log_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Audit log not found")
        
        log_data = response.data[0]
        # Check tenant access (super admin can access any, others only their tenant)
        if current_user.role != "super_admin":
            if log_data.get("tenant_id") and UUID(log_data["tenant_id"]) != tenant_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        return log_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit log: {str(e)}")


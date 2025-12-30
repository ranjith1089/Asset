from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable
from app.database import supabase
from app.models.user import User
from app.utils.auth import get_current_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
import time

security = HTTPBearer(auto_error=False)


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests for audit purposes"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        path = str(request.url.path)
        
        # Skip audit logging for health checks, static files, and public auth endpoints
        if path in ["/health", "/", "/docs", "/openapi.json", "/redoc"] or path.startswith("/api/auth/"):
            return await call_next(request)
        
        # Get user info if authenticated
        user_id = None
        tenant_id = None
        try:
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                token = authorization.split(" ")[1]
                credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
                user = await get_current_user(credentials)
                user_id = str(user.id)
                tenant_id = str(user.tenant_id) if user.tenant_id else None
        except Exception:
            # Not authenticated or error getting user - continue without audit log
            pass
        
        # Process request
        response = await call_next(request)
        
        # Log audit entry for authenticated users
        if user_id and response.status_code < 500:  # Don't log server errors
            try:
                # Determine action and resource from request
                action = request.method.lower()
                resource_type = request.url.path.split("/")[-1] if request.url.path else None
                
                # Extract resource ID if present in path
                resource_id = None
                path_parts = [p for p in request.url.path.split("/") if p]
                if len(path_parts) >= 2:
                    try:
                        from uuid import UUID
                        resource_id = str(UUID(path_parts[-1]))
                    except (ValueError, IndexError):
                        pass
                
                # Prepare audit log entry
                audit_data = {
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "details": {
                        "path": request.url.path,
                        "method": request.method,
                        "status_code": response.status_code,
                        "duration_ms": round((time.time() - start_time) * 1000, 2)
                    },
                    "ip_address": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent")
                }
                
                # Insert audit log (non-blocking - don't fail request if logging fails)
                try:
                    supabase.table("audit_logs").insert(audit_data).execute()
                except Exception:
                    # Silently fail audit logging to not break the request
                    pass
            except Exception:
                # Silently fail audit logging
                pass
        
        return response


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to inject tenant context into request state"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip tenant context for public auth endpoints
        path = str(request.url.path)
        if path.startswith("/api/auth/"):
            return await call_next(request)
        
        # Get tenant from user if authenticated
        try:
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                token = authorization.split(" ")[1]
                credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
                user = await get_current_user(credentials)
                if user.tenant_id:
                    request.state.tenant_id = user.tenant_id
                    request.state.user_role = user.role
        except Exception:
            # Not authenticated - continue without tenant context
            pass
        
        return await call_next(request)


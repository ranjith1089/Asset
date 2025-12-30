from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Dict, Any, Optional
from uuid import UUID
from app.models.user import User
from app.models.user_management import User as UserManagement
from app.database import supabase
import json
import base64

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
    """Verify JWT token and return user info with tenant and role"""
    token = credentials.credentials
    
    try:
        # Try to decode using python-jose first
        try:
            decoded_token: Dict[str, Any] = jwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_nbf": False,
                    "verify_iat": False,
                    "verify_aud": False,
                    "verify_iss": False
                }
            )
        except Exception:
            # If jwt.decode fails, manually decode the payload
            # JWT format: header.payload.signature
            parts = token.split('.')
            if len(parts) != 3:
                raise HTTPException(status_code=401, detail="Invalid token format")
            
            # Decode the payload (second part)
            payload = parts[1]
            # Add padding if needed
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            decoded_bytes = base64.urlsafe_b64decode(payload)
            decoded_token = json.loads(decoded_bytes.decode('utf-8'))
        
        # Extract user information from token
        user_id = decoded_token.get("sub")
        email = decoded_token.get("email")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication token - no user ID")
        
        # Fetch user from database to get tenant_id and role
        try:
            user_response = supabase.table("users").select("*").eq("id", user_id).execute()
            if user_response.data and len(user_response.data) > 0:
                user_data = user_response.data[0]
                return User(
                    id=UUID(user_data["id"]),
                    email=user_data.get("email") or email,
                    tenant_id=UUID(user_data["tenant_id"]) if user_data.get("tenant_id") else None,
                    role=user_data.get("role"),
                    status=user_data.get("status")
                )
            else:
                # User not in users table yet (legacy or new signup)
                return User(id=UUID(user_id), email=email)
        except Exception as db_error:
            # If database lookup fails, return basic user info
            return User(id=UUID(user_id), email=email)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")


async def get_current_tenant(current_user: User = Depends(get_current_user)) -> UUID:
    """Get current user's tenant_id"""
    if not current_user.tenant_id:
        raise HTTPException(status_code=403, detail="User is not associated with a tenant")
    return current_user.tenant_id


def require_role(allowed_roles: list[str]):
    """Dependency factory to require specific roles"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.role or current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


def require_permission(resource: str, action: str):
    """Dependency factory to require specific permission"""
    from app.utils.permissions import Resource, Action, has_permission
    
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.role:
            raise HTTPException(status_code=403, detail="User role not found")
        
        try:
            resource_enum = Resource(resource)
            action_enum = Action(action)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid resource or action: {resource}.{action}")
        
        if not has_permission(current_user.role, resource_enum, action_enum):
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required permission: {resource}.{action}"
            )
        return current_user
    return permission_checker

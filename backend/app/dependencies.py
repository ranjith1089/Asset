from fastapi import Depends
from app.utils.auth import get_current_user, get_current_tenant
from app.models.user import User
from uuid import UUID


def get_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get current authenticated user"""
    return current_user


def get_tenant(tenant_id: UUID = Depends(get_current_tenant)) -> UUID:
    """Dependency to get current user's tenant_id"""
    return tenant_id


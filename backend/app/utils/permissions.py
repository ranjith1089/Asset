from typing import Dict, Any, List
from enum import Enum


class Resource(str, Enum):
    ASSETS = "assets"
    EMPLOYEES = "employees"
    ASSIGNMENTS = "assignments"
    USERS = "users"
    ROLES = "roles"
    SETTINGS = "settings"
    AUDIT_LOGS = "audit_logs"
    TENANTS = "tenants"


class Action(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE = "manage"


# Default permission matrix for system roles
DEFAULT_PERMISSIONS = {
    "super_admin": {
        Resource.ASSETS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE],
        Resource.EMPLOYEES: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE],
        Resource.ASSIGNMENTS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE],
        Resource.USERS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE],
        Resource.ROLES: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE],
        Resource.SETTINGS: [Action.READ, Action.UPDATE],
        Resource.AUDIT_LOGS: [Action.READ],
        Resource.TENANTS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE],
    },
    "tenant_admin": {
        Resource.ASSETS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE],
        Resource.EMPLOYEES: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE],
        Resource.ASSIGNMENTS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE],
        Resource.USERS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE],
        Resource.ROLES: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
        Resource.SETTINGS: [Action.READ, Action.UPDATE],
        Resource.AUDIT_LOGS: [Action.READ],
    },
    "manager": {
        Resource.ASSETS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
        Resource.EMPLOYEES: [Action.CREATE, Action.READ, Action.UPDATE],
        Resource.ASSIGNMENTS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
        Resource.USERS: [Action.READ],
        Resource.ROLES: [Action.READ],
        Resource.SETTINGS: [Action.READ],
        Resource.AUDIT_LOGS: [Action.READ],
    },
    "staff": {
        Resource.ASSETS: [Action.READ, Action.UPDATE],
        Resource.EMPLOYEES: [Action.READ],
        Resource.ASSIGNMENTS: [Action.CREATE, Action.READ, Action.UPDATE],
        Resource.USERS: [Action.READ],
        Resource.ROLES: [Action.READ],
        Resource.SETTINGS: [Action.READ],
    },
    "viewer": {
        Resource.ASSETS: [Action.READ],
        Resource.EMPLOYEES: [Action.READ],
        Resource.ASSIGNMENTS: [Action.READ],
        Resource.USERS: [Action.READ],
        Resource.ROLES: [Action.READ],
        Resource.SETTINGS: [Action.READ],
    },
}


def has_permission(role: str, resource: Resource, action: Action, custom_permissions: Dict[str, Any] = None) -> bool:
    """
    Check if a role has permission for a resource and action.
    
    Args:
        role: User role (super_admin, tenant_admin, manager, staff, viewer)
        resource: Resource to check
        action: Action to check
        custom_permissions: Optional custom permissions dict (from roles table)
    
    Returns:
        True if permission exists, False otherwise
    """
    # Super admin has all permissions
    if role == "super_admin":
        return True
    
    # Check custom permissions first if provided
    if custom_permissions:
        resource_perms = custom_permissions.get(resource.value, [])
        if isinstance(resource_perms, list):
            return action.value in resource_perms or Action.MANAGE.value in resource_perms
        return False
    
    # Check default permissions
    role_perms = DEFAULT_PERMISSIONS.get(role, {})
    resource_perms = role_perms.get(resource, [])
    
    # If MANAGE is in permissions, user has all actions
    if Action.MANAGE in resource_perms:
        return True
    
    return action in resource_perms


def get_role_permissions(role: str) -> Dict[str, List[str]]:
    """
    Get all permissions for a role.
    
    Args:
        role: User role
    
    Returns:
        Dictionary mapping resources to list of allowed actions
    """
    if role == "super_admin":
        # Super admin has all permissions
        return {resource.value: [action.value for action in Action] for resource in Resource}
    
    role_perms = DEFAULT_PERMISSIONS.get(role, {})
    return {
        resource.value: [action.value for action in actions]
        for resource, actions in role_perms.items()
    }


def check_permission(user_role: str, resource: Resource, action: Action, custom_permissions: Dict[str, Any] = None) -> bool:
    """
    Alias for has_permission for backward compatibility.
    """
    return has_permission(user_role, resource, action, custom_permissions)


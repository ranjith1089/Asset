import React from 'react';
import { useAuth } from '../../hooks/useAuth';

interface PermissionGateProps {
  resource: string;
  action: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

const PermissionGate: React.FC<PermissionGateProps> = ({
  resource,
  action,
  children,
  fallback = null,
}) => {
  const { userInfo } = useAuth();

  // Super admin has all permissions
  if (userInfo?.role === 'super_admin') {
    return <>{children}</>;
  }

  // Default permission matrix (simplified - in production, fetch from API)
  const hasPermission = () => {
    const role = userInfo?.role || 'viewer';
    
    // Tenant admin has most permissions
    if (role === 'tenant_admin') {
      return true; // Tenant admin has all permissions within tenant
    }

    // Manager permissions
    if (role === 'manager') {
      const managerResources = ['assets', 'employees', 'assignments'];
      return managerResources.includes(resource);
    }

    // Staff permissions
    if (role === 'staff') {
      const staffRead = ['assets', 'employees', 'assignments'];
      return staffRead.includes(resource) && action === 'read';
    }

    // Viewer - read only
    if (role === 'viewer') {
      return action === 'read';
    }

    return false;
  };

  return hasPermission() ? <>{children}</> : <>{fallback}</>;
};

export default PermissionGate;


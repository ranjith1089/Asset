import React from 'react';
import { useAuth } from '../../hooks/useAuth';

interface RoleSelectorProps {
  value: string;
  onChange: (role: string) => void;
  disabled?: boolean;
}

const RoleSelector: React.FC<RoleSelectorProps> = ({ value, onChange, disabled = false }) => {
  const { userInfo } = useAuth();
  const isSuperAdmin = userInfo?.role === 'super_admin';

  const roles = [
    { value: 'viewer', label: 'Viewer' },
    { value: 'staff', label: 'Staff' },
    { value: 'manager', label: 'Manager' },
    { value: 'tenant_admin', label: 'Tenant Admin' },
    ...(isSuperAdmin ? [{ value: 'super_admin', label: 'Super Admin' }] : []),
  ];

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
    >
      {roles.map((role) => (
        <option key={role.value} value={role.value}>
          {role.label}
        </option>
      ))}
    </select>
  );
};

export default RoleSelector;


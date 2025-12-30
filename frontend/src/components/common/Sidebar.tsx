import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

interface SidebarProps {
  currentPath: string;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPath }) => {
  const { userInfo, user } = useAuth();
  // Try to get role from userInfo first, then fall back to JWT token if available
  const role = userInfo?.role || (user?.user_metadata?.role as string) || 'viewer';

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊', roles: ['super_admin', 'tenant_admin', 'manager', 'staff', 'viewer'] },
    { path: '/assets', label: 'Assets', icon: '💻', roles: ['super_admin', 'tenant_admin', 'manager', 'staff', 'viewer'] },
    { path: '/employees', label: 'Employees', icon: '👥', roles: ['super_admin', 'tenant_admin', 'manager', 'staff', 'viewer'] },
    { path: '/assignments', label: 'Assignments', icon: '📋', roles: ['super_admin', 'tenant_admin', 'manager', 'staff', 'viewer'] },
    { path: '/users', label: 'Users', icon: '👤', roles: ['super_admin', 'tenant_admin'] },
    { path: '/roles', label: 'Roles', icon: '🔐', roles: ['super_admin', 'tenant_admin'] },
    { path: '/settings', label: 'Settings', icon: '⚙️', roles: ['super_admin', 'tenant_admin'] },
  ].filter(item => item.roles.includes(role));

  return (
    <aside className="w-64 bg-white shadow-sm min-h-screen">
      <nav className="p-4">
        <ul className="space-y-2">
          {navItems.map((item) => {
            const isActive = currentPath === item.path;
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-100 text-blue-700 font-semibold'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <span className="text-xl">{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;


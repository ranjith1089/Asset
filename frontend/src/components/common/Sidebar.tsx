import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

interface SidebarProps {
  currentPath: string;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPath }) => {
  const { userInfo, user } = useAuth();
  
  // Try to get role from userInfo first (from API), then fall back to JWT token metadata
  let role = userInfo?.role;
  
  if (!role && user) {
    // Try to get role from user metadata
    const metadata = (user as any).user_metadata;
    role = metadata?.role;
    
    // If still no role but user is logged in, default to tenant_admin for now
    // This handles the case where userInfo hasn't loaded yet but user is authenticated
    if (!role && user) {
      role = 'tenant_admin'; // Safe default for logged-in users
    }
  }
  
  role = role || 'viewer';

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


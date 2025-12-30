import React, { useState, useEffect } from 'react';
import { rolesService } from '../services/roles';
import { Role, RoleCreate } from '../types/role';
import { useAuth } from '../hooks/useAuth';

const RESOURCES = ['assets', 'employees', 'assignments', 'users', 'roles', 'settings', 'audit_logs'];
const ACTIONS = ['create', 'read', 'update', 'delete', 'manage'];

const Roles: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const { userInfo } = useAuth();

  const [formData, setFormData] = useState<RoleCreate>({
    name: '',
    permissions: {},
  });

  useEffect(() => {
    fetchRoles();
  }, []);

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const data = await rolesService.getAll();
      setRoles(data);
    } catch (error) {
      console.error('Error fetching roles:', error);
      alert('Failed to load roles');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingRole(null);
    setFormData({
      name: '',
      permissions: {},
    });
    setShowForm(true);
  };

  const handleEdit = (role: Role) => {
    setEditingRole(role);
    setFormData({
      name: role.name,
      permissions: role.permissions,
    });
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingRole) {
        await rolesService.update(editingRole.id, formData);
      } else {
        await rolesService.create(formData);
      }
      setShowForm(false);
      fetchRoles();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to save role');
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this role?')) return;
    try {
      await rolesService.delete(id);
      fetchRoles();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete role');
    }
  };

  const togglePermission = (resource: string, action: string) => {
    const currentPerms = formData.permissions[resource] || [];
    let newPerms: string[];
    
    if (action === 'manage') {
      // Manage gives all permissions
      newPerms = currentPerms.includes('manage') ? [] : ['manage'];
    } else {
      // Toggle specific action
      if (currentPerms.includes('manage')) {
        // If manage is set, remove it and add all specific actions
        newPerms = ACTIONS.filter(a => a !== 'manage');
      } else if (currentPerms.includes(action)) {
        newPerms = currentPerms.filter(a => a !== action);
      } else {
        newPerms = [...currentPerms, action];
      }
    }
    
    setFormData({
      ...formData,
      permissions: {
        ...formData.permissions,
        [resource]: newPerms,
      },
    });
  };

  const canManageRoles = userInfo?.role === 'tenant_admin' || userInfo?.role === 'super_admin';

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Roles</h1>
        {canManageRoles && (
          <button
            onClick={handleCreate}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            + Create Role
          </button>
        )}
      </div>

      {showForm && canManageRoles && (
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-6 space-y-4">
          <h2 className="text-2xl font-bold mb-4">
            {editingRole ? 'Edit Role' : 'Create Role'}
          </h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Permissions</label>
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Resource</th>
                    {ACTIONS.map((action) => (
                      <th key={action} className="px-4 py-2 text-center text-sm font-medium text-gray-700">
                        {action.charAt(0).toUpperCase() + action.slice(1)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {RESOURCES.map((resource) => {
                    const resourcePerms = formData.permissions[resource] || [];
                    const hasManage = resourcePerms.includes('manage');
                    return (
                      <tr key={resource}>
                        <td className="px-4 py-2 text-sm font-medium text-gray-900 capitalize">
                          {resource.replace('_', ' ')}
                        </td>
                        {ACTIONS.map((action) => {
                          const isChecked =
                            hasManage || resourcePerms.includes(action);
                          return (
                            <td key={action} className="px-4 py-2 text-center">
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={() => togglePermission(resource, action)}
                                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                              />
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              {editingRole ? 'Update Role' : 'Create Role'}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="text-center py-8">Loading roles...</div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Permissions</th>
                {canManageRoles && (
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                )}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {roles.map((role) => (
                <tr key={role.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {role.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        role.is_system_role
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {role.is_system_role ? 'System' : 'Custom'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {Object.keys(role.permissions).length} resource(s)
                  </td>
                  {canManageRoles && !role.is_system_role && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      <button
                        onClick={() => handleEdit(role)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(role.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  )}
                  {canManageRoles && role.is_system_role && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      System role
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Roles;


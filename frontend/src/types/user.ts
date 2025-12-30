export interface User {
  id: string;
  tenant_id: string;
  name: string;
  email: string;
  mobile?: string;
  role: 'super_admin' | 'tenant_admin' | 'manager' | 'staff' | 'viewer';
  status: 'active' | 'inactive' | 'suspended';
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  name: string;
  email: string;
  mobile?: string;
  password?: string;
  role?: 'super_admin' | 'tenant_admin' | 'manager' | 'staff' | 'viewer';
  status?: 'active' | 'inactive' | 'suspended';
}

export interface UserUpdate {
  name?: string;
  mobile?: string;
  role?: 'super_admin' | 'tenant_admin' | 'manager' | 'staff' | 'viewer';
  status?: 'active' | 'inactive' | 'suspended';
}


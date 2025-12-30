export interface Role {
  id: string;
  tenant_id: string;
  name: string;
  permissions: Record<string, string[]>;
  is_system_role: boolean;
  created_at: string;
  updated_at: string;
}

export interface RoleCreate {
  name: string;
  permissions: Record<string, string[]>;
  is_system_role?: boolean;
}

export interface RoleUpdate {
  name?: string;
  permissions?: Record<string, string[]>;
}


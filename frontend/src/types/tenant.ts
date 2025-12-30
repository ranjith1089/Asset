export interface Tenant {
  id: string;
  name: string;
  slug: string;
  logo_url?: string;
  theme?: Record<string, any>;
  status: 'active' | 'suspended' | 'deleted';
  subscription_plan: 'free' | 'trial' | 'basic' | 'premium' | 'enterprise';
  subscription_status: 'active' | 'cancelled' | 'expired';
  subscription_expires_at?: string;
  settings?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface TenantCreate {
  name: string;
  slug?: string;
  logo_url?: string;
  theme?: Record<string, any>;
  settings?: Record<string, any>;
}

export interface TenantUpdate {
  name?: string;
  logo_url?: string;
  theme?: Record<string, any>;
  settings?: Record<string, any>;
  status?: 'active' | 'suspended' | 'deleted';
}


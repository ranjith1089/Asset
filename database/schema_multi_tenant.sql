-- Multi-Tenant Asset Management System Database Schema
-- Run this SQL in your Supabase SQL Editor
-- This schema adds multi-tenancy support to the existing system

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- NEW TABLES FOR MULTI-TENANCY
-- ============================================================================

-- Tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    logo_url VARCHAR(500),
    theme JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    subscription_plan VARCHAR(50) DEFAULT 'free' CHECK (subscription_plan IN ('free', 'trial', 'basic', 'premium', 'enterprise')),
    subscription_status VARCHAR(50) DEFAULT 'active' CHECK (subscription_status IN ('active', 'cancelled', 'expired')),
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    mobile VARCHAR(50),
    role VARCHAR(50) NOT NULL DEFAULT 'staff' CHECK (role IN ('super_admin', 'tenant_admin', 'manager', 'staff', 'viewer')),
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Roles table (custom roles per tenant)
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    permissions JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

-- Permissions table (permission definitions)
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(resource, action)
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB DEFAULT '{}'::jsonb,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL UNIQUE REFERENCES tenants(id) ON DELETE CASCADE,
    plan VARCHAR(50) NOT NULL CHECK (plan IN ('free', 'trial', 'basic', 'premium', 'enterprise')),
    status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired')),
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed')),
    due_date TIMESTAMP WITH TIME ZONE,
    paid_at TIMESTAMP WITH TIME ZONE,
    invoice_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MODIFY EXISTING TABLES FOR MULTI-TENANCY
-- ============================================================================

-- Add tenant_id to employees table
ALTER TABLE employees ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
-- Make tenant_id NOT NULL after migration
-- ALTER TABLE employees ALTER COLUMN tenant_id SET NOT NULL;

-- Add tenant_id to assets table
ALTER TABLE assets ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
-- Make tenant_id NOT NULL after migration
-- ALTER TABLE assets ALTER COLUMN tenant_id SET NOT NULL;

-- Add tenant_id to assignments table
ALTER TABLE assignments ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
-- Make tenant_id NOT NULL after migration
-- ALTER TABLE assignments ALTER COLUMN tenant_id SET NOT NULL;

-- ============================================================================
-- UPDATE UNIQUE CONSTRAINTS FOR MULTI-TENANCY
-- ============================================================================

-- Drop old unique constraints
ALTER TABLE employees DROP CONSTRAINT IF EXISTS employees_email_key;
ALTER TABLE assets DROP CONSTRAINT IF EXISTS assets_asset_tag_key;

-- Add tenant-scoped unique constraints
CREATE UNIQUE INDEX IF NOT EXISTS idx_employees_tenant_email ON employees(tenant_id, email) WHERE email IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_assets_tenant_tag ON assets(tenant_id, asset_tag);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Tenant indexes
CREATE INDEX IF NOT EXISTS idx_tenants_slug ON tenants(slug);
CREATE INDEX IF NOT EXISTS idx_tenants_status ON tenants(status);

-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_users_tenant_role ON users(tenant_id, role);

-- Role indexes
CREATE INDEX IF NOT EXISTS idx_roles_tenant_id ON roles(tenant_id);

-- Audit log indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- Subscription indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant_id ON subscriptions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

-- Invoice indexes
CREATE INDEX IF NOT EXISTS idx_invoices_tenant_id ON invoices(tenant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);

-- Updated composite indexes for existing tables
CREATE INDEX IF NOT EXISTS idx_employees_tenant_id ON employees(tenant_id);
CREATE INDEX IF NOT EXISTS idx_employees_tenant_email ON employees(tenant_id, email);
CREATE INDEX IF NOT EXISTS idx_assets_tenant_id ON assets(tenant_id);
CREATE INDEX IF NOT EXISTS idx_assets_tenant_status ON assets(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_assignments_tenant_id ON assignments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_assignments_tenant_status ON assignments(tenant_id, status);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for new tables
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

-- Tenants policies
CREATE POLICY "Users can view their own tenant"
    ON tenants FOR SELECT
    TO authenticated
    USING (
        id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

CREATE POLICY "Super admins can manage all tenants"
    ON tenants FOR ALL
    TO authenticated
    USING (EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin'));

-- Users policies
CREATE POLICY "Users can view users in their tenant"
    ON users FOR SELECT
    TO authenticated
    USING (
        tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

CREATE POLICY "Tenant admins can manage users in their tenant"
    ON users FOR ALL
    TO authenticated
    USING (
        (tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid()) 
         AND EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('tenant_admin', 'super_admin')))
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

-- Roles policies
CREATE POLICY "Users can view roles in their tenant"
    ON roles FOR SELECT
    TO authenticated
    USING (
        tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

CREATE POLICY "Tenant admins can manage roles in their tenant"
    ON roles FOR ALL
    TO authenticated
    USING (
        (tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid()) 
         AND EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('tenant_admin', 'super_admin')))
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

-- Permissions policies (read-only for all authenticated users)
CREATE POLICY "Authenticated users can read permissions"
    ON permissions FOR SELECT
    TO authenticated
    USING (true);

-- Audit logs policies
CREATE POLICY "Users can view audit logs in their tenant"
    ON audit_logs FOR SELECT
    TO authenticated
    USING (
        tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
        OR user_id = auth.uid()
    );

-- Subscriptions policies
CREATE POLICY "Users can view subscription for their tenant"
    ON subscriptions FOR SELECT
    TO authenticated
    USING (
        tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

-- Invoices policies
CREATE POLICY "Users can view invoices for their tenant"
    ON invoices FOR SELECT
    TO authenticated
    USING (
        tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

-- Updated RLS policies for existing tables (tenant-scoped)
DROP POLICY IF EXISTS "Allow authenticated users to read employees" ON employees;
DROP POLICY IF EXISTS "Allow authenticated users to insert employees" ON employees;
DROP POLICY IF EXISTS "Allow authenticated users to update employees" ON employees;
DROP POLICY IF EXISTS "Allow authenticated users to delete employees" ON employees;

DROP POLICY IF EXISTS "Allow authenticated users to read assets" ON assets;
DROP POLICY IF EXISTS "Allow authenticated users to insert assets" ON assets;
DROP POLICY IF EXISTS "Allow authenticated users to update assets" ON assets;
DROP POLICY IF EXISTS "Allow authenticated users to delete assets" ON assets;

DROP POLICY IF EXISTS "Allow authenticated users to read assignments" ON assignments;
DROP POLICY IF EXISTS "Allow authenticated users to insert assignments" ON assignments;
DROP POLICY IF EXISTS "Allow authenticated users to update assignments" ON assignments;
DROP POLICY IF EXISTS "Allow authenticated users to delete assignments" ON assignments;

-- Employees policies (tenant-scoped)
CREATE POLICY "Users can view employees in their tenant"
    ON employees FOR SELECT
    TO authenticated
    USING (
        tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

CREATE POLICY "Users can manage employees in their tenant"
    ON employees FOR ALL
    TO authenticated
    USING (
        tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

-- Assets policies (tenant-scoped)
CREATE POLICY "Users can view assets in their tenant"
    ON assets FOR SELECT
    TO authenticated
    USING (
        tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

CREATE POLICY "Users can manage assets in their tenant"
    ON assets FOR ALL
    TO authenticated
    USING (
        tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

-- Assignments policies (tenant-scoped)
CREATE POLICY "Users can view assignments in their tenant"
    ON assignments FOR SELECT
    TO authenticated
    USING (
        tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

CREATE POLICY "Users can manage assignments in their tenant"
    ON assignments FOR ALL
    TO authenticated
    USING (
        tenant_id IN (SELECT tenant_id FROM users WHERE id = auth.uid())
        OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'super_admin')
    );

-- ============================================================================
-- DEFAULT DATA
-- ============================================================================

-- Insert default permissions
INSERT INTO permissions (resource, action, description) VALUES
    ('assets', 'create', 'Create new assets'),
    ('assets', 'read', 'View assets'),
    ('assets', 'update', 'Update assets'),
    ('assets', 'delete', 'Delete assets'),
    ('assets', 'manage', 'Full management of assets'),
    ('employees', 'create', 'Create new employees'),
    ('employees', 'read', 'View employees'),
    ('employees', 'update', 'Update employees'),
    ('employees', 'delete', 'Delete employees'),
    ('employees', 'manage', 'Full management of employees'),
    ('assignments', 'create', 'Create new assignments'),
    ('assignments', 'read', 'View assignments'),
    ('assignments', 'update', 'Update assignments'),
    ('assignments', 'delete', 'Delete assignments'),
    ('assignments', 'manage', 'Full management of assignments'),
    ('users', 'create', 'Create new users'),
    ('users', 'read', 'View users'),
    ('users', 'update', 'Update users'),
    ('users', 'delete', 'Delete users'),
    ('users', 'manage', 'Full management of users'),
    ('roles', 'create', 'Create new roles'),
    ('roles', 'read', 'View roles'),
    ('roles', 'update', 'Update roles'),
    ('roles', 'delete', 'Delete roles'),
    ('settings', 'read', 'View settings'),
    ('settings', 'update', 'Update settings'),
    ('audit_logs', 'read', 'View audit logs')
ON CONFLICT (resource, action) DO NOTHING;


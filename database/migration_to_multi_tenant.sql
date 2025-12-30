-- Migration Script: Convert Single-Tenant to Multi-Tenant
-- Run this AFTER running schema_multi_tenant.sql
-- This script migrates existing data to a default tenant

-- Step 1: Create a default tenant for existing data
DO $$
DECLARE
    default_tenant_id UUID;
BEGIN
    -- Create default tenant
    INSERT INTO tenants (name, slug, status, subscription_plan, subscription_status)
    VALUES ('Default Organization', 'default-org', 'active', 'free', 'active')
    ON CONFLICT (slug) DO NOTHING
    RETURNING id INTO default_tenant_id;
    
    -- If tenant already exists, get its ID
    IF default_tenant_id IS NULL THEN
        SELECT id INTO default_tenant_id FROM tenants WHERE slug = 'default-org';
    END IF;
    
    -- Step 2: Assign all existing employees to default tenant
    UPDATE employees 
    SET tenant_id = default_tenant_id 
    WHERE tenant_id IS NULL;
    
    -- Step 3: Assign all existing assets to default tenant
    UPDATE assets 
    SET tenant_id = default_tenant_id 
    WHERE tenant_id IS NULL;
    
    -- Step 4: Assign all existing assignments to default tenant
    UPDATE assignments 
    SET tenant_id = default_tenant_id 
    WHERE tenant_id IS NULL;
    
    -- Step 5: Create default roles for the tenant
    INSERT INTO roles (tenant_id, name, permissions, is_system_role)
    VALUES 
        (default_tenant_id, 'Tenant Admin', 
         '{"assets": ["create", "read", "update", "delete", "manage"], "employees": ["create", "read", "update", "delete", "manage"], "assignments": ["create", "read", "update", "delete", "manage"], "users": ["create", "read", "update", "delete", "manage"], "roles": ["create", "read", "update", "delete"], "settings": ["read", "update"], "audit_logs": ["read"]}'::jsonb,
         true),
        (default_tenant_id, 'Manager',
         '{"assets": ["create", "read", "update", "delete"], "employees": ["create", "read", "update"], "assignments": ["create", "read", "update", "delete"], "users": ["read"], "roles": ["read"], "settings": ["read"], "audit_logs": ["read"]}'::jsonb,
         true),
        (default_tenant_id, 'Staff',
         '{"assets": ["read", "update"], "employees": ["read"], "assignments": ["create", "read", "update"], "users": ["read"], "roles": ["read"], "settings": ["read"]}'::jsonb,
         true),
        (default_tenant_id, 'Viewer',
         '{"assets": ["read"], "employees": ["read"], "assignments": ["read"], "users": ["read"], "roles": ["read"], "settings": ["read"]}'::jsonb,
         true)
    ON CONFLICT (tenant_id, name) DO NOTHING;
    
    -- Step 6: Create default subscription
    INSERT INTO subscriptions (tenant_id, plan, status, current_period_start, current_period_end)
    VALUES (default_tenant_id, 'free', 'active', NOW(), NOW() + INTERVAL '1 year')
    ON CONFLICT (tenant_id) DO NOTHING;
    
    RAISE NOTICE 'Migration completed. Default tenant ID: %', default_tenant_id;
END $$;

-- Step 7: Make tenant_id columns NOT NULL (after data migration)
-- Uncomment these after verifying the migration worked:
-- ALTER TABLE employees ALTER COLUMN tenant_id SET NOT NULL;
-- ALTER TABLE assets ALTER COLUMN tenant_id SET NOT NULL;
-- ALTER TABLE assignments ALTER COLUMN tenant_id SET NOT NULL;

-- Step 8: Note for manual step
-- After running this migration, you need to:
-- 1. Create user records in the users table for existing Supabase auth users
-- 2. Assign them to the default tenant with appropriate roles
-- This can be done via the API or manually:
-- INSERT INTO users (id, tenant_id, name, email, role, status)
-- SELECT id, (SELECT id FROM tenants WHERE slug = 'default-org'), 
--        raw_user_meta_data->>'name' as name,
--        email,
--        'tenant_admin' as role,
--        'active' as status
-- FROM auth.users
-- WHERE NOT EXISTS (SELECT 1 FROM users WHERE users.id = auth.users.id);


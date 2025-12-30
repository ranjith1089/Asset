from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import (
    assets, employees, assignments, test,
    auth_routes, tenants, users, roles, subscriptions, audit
)
from app.utils.middleware import AuditLogMiddleware, TenantContextMiddleware
import sys

# Validate configuration on startup
def validate_config():
    """Validate that all required configuration is present"""
    missing_vars = []
    if not settings.supabase_url:
        missing_vars.append("SUPABASE_URL")
    if not settings.supabase_key:
        missing_vars.append("SUPABASE_KEY")
    if not settings.supabase_service_key:
        missing_vars.append("SUPABASE_SERVICE_KEY")
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in Railway dashboard: Settings > Variables")
        sys.exit(1)

# Validate before creating the app
validate_config()

app = FastAPI(
    title="Multi-Tenant Asset Management API",
    description="Multi-tenant SaaS API for managing office assets and employee assignments",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
# Note: Middleware executes in reverse order (last added = first executed)
# So AuditLogMiddleware runs first, then TenantContextMiddleware
app.add_middleware(AuditLogMiddleware)
app.add_middleware(TenantContextMiddleware)

# Include routers
# Authentication routes (public)
app.include_router(auth_routes.router, prefix="/api")

# Core resource routes (tenant-scoped)
app.include_router(assets.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(assignments.router, prefix="/api")

# Multi-tenant management routes
app.include_router(tenants.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(roles.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(audit.router, prefix="/api")

# Test route
app.include_router(test.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Multi-Tenant Asset Management API", "version": "2.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


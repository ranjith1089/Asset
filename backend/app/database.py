from supabase import create_client, Client
from app.config import settings

# Use service role key for backend operations (bypasses RLS)
# We've already authenticated the user in our middleware
try:
    supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)
except Exception as e:
    print(f"ERROR: Failed to initialize Supabase client")
    print(f"Supabase URL: {settings.supabase_url[:50]}..." if settings.supabase_url else "Supabase URL: NOT SET")
    print(f"Error details: {str(e)}")
    raise


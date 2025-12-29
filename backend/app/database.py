from supabase import create_client, Client
from app.config import settings

# Use service role key for backend operations (bypasses RLS)
# We've already authenticated the user in our middleware
supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)


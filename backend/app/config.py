from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",")]
        # Also allow all origins in development (you can remove this in production for security)
        # For now, let's keep it strict but log what we're allowing
        return origins
    
    class Config:
        env_file = ".env"


try:
    settings = Settings()
except Exception as e:
    print(f"ERROR: Failed to load settings. Missing required environment variables.")
    print(f"Required variables: SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY, CORS_ORIGINS (optional)")
    print(f"Error details: {str(e)}")
    raise


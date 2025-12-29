from typing import Optional


class User:
    """Simple user model for authentication"""
    def __init__(self, id: str, email: Optional[str] = None):
        self.id = id
        self.email = email


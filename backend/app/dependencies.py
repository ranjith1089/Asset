from fastapi import Depends
from app.utils.auth import get_current_user
from app.models.user import User


def get_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get current authenticated user"""
    return current_user


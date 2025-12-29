from fastapi import APIRouter, Depends
from app.dependencies import get_user
from app.models.user import User

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/auth")
async def test_auth(current_user: User = Depends(get_user)):
    """Test endpoint to verify authentication is working"""
    return {
        "message": "Authentication successful!",
        "user_id": current_user.id,
        "email": current_user.email
    }


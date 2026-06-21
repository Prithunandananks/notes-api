from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserRead, summary="Get Current User Profile")
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    """
    Returns the profile metadata of the currently authenticated active user.
    """
    return current_user

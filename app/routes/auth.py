from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limiter import limiter
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token
from app.services.user import user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED, summary="Register User")
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new user account with secure password hashing.
    Checks for email uniqueness before registration.
    """
    return await user_service.register_user(db, user_in)

@router.post("/login", response_model=Token, summary="Login User")
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates login credentials and generates an OAuth2-compliant JWT Access Token.
    Accepts standard form-data with username (email) and password.
    """
    user = await user_service.authenticate(db, email=form_data.username, password=form_data.password)
    return user_service.generate_token(user)

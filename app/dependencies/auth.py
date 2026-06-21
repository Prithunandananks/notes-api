from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import oauth2_scheme, decode_access_token
from app.models.user import User

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Extracts, validates, and decodes the JWT bearer token from the request headers.
    Retrieves the corresponding User object from the database.
    
    Raises:
        HTTPException: 401 Unauthorized if the token is invalid, expired, malformed,
                       or if the user no longer exists in the system database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Decode and validate access token claims
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception
        
    # 2. Fetch the corresponding user from the database using SQLAlchemy 2.0 select query
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    # 3. Handle missing user case (e.g. user was deleted from the system)
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Validates that the authenticated user account is active.
    
    Raises:
        HTTPException: 403 Forbidden if the user is flagged as inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user

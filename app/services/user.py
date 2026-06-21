from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.repositories.user import user_repository
from app.schemas.user import UserCreate
from app.schemas.token import Token

class UserService:
    """
    User business logic service.
    Orchestrates authentication, validation, registration, and token generation.
    """
    async def register_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        """
        Validates email uniqueness and registers a new user with a hashed password.
        Raises:
            BadRequestException: If the email address is already taken.
        """
        if await user_repository.check_email_exists(db, user_in.email):
            raise BadRequestException("A user with this email already exists.")
            
        hashed_pwd = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_pwd
        )
        return await user_repository.create(db, db_obj=db_user)

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> User:
        """
        Verifies login credentials.
        Raises:
            BadRequestException: If email/password are incorrect (maps to HTTP 400 for OAuth2/test compatibility).
            UnauthorizedException: If the user account is flagged as inactive.
        """
        user = await user_repository.get_by_email(db, email)
        if not user:
            raise BadRequestException("Incorrect email or password")
            
        if not verify_password(password, user.hashed_password):
            raise BadRequestException("Incorrect email or password")
            
        if not user.is_active:
            raise UnauthorizedException("User account is inactive")
            
        return user

    def generate_token(self, user: User) -> Token:
        """
        Generates a standard OAuth2 JWT bearer access token for a validated user.
        """
        access_token = create_access_token(subject=user.id)
        return Token(access_token=access_token, token_type="bearer")

user_service = UserService()

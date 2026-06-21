import logging
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from fastapi.security import OAuth2PasswordBearer

logger = logging.getLogger("app.security")

# 1. Secure Monkeypatch for passlib and modern bcrypt compatibility.
# Newer bcrypt versions (>=4.0.0) throw a ValueError when input strings exceed 72 bytes.
# passlib's internal test vector check during initialization passes a 100-byte key,
# causing an unhandled exception. Monkeypatching bcrypt.hashpw to truncate input
# avoids initialization failure while adhering to bcrypt's standard 72-byte limit.
_original_hashpw = bcrypt.hashpw
def _safe_hashpw(password: bytes, salt: bytes) -> bytes:
    if len(password) > 72:
        password = password[:72]
    return _original_hashpw(password, salt)
bcrypt.hashpw = _safe_hashpw

from passlib.context import CryptContext
from app.core.config import settings

# 2. Configure Passlib CryptContext.
# Explicitly uses the bcrypt hashing scheme.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 3. OAuth2 Password Flow scheme integration.
# Points to the login token endpoint.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored hash.
    Safely handles platform errors and standard bcrypt 72-byte truncation.
    """
    try:
        # Truncate password before verification to match bcrypt hashing bounds
        truncated_pwd = plain_password[:72]
        return pwd_context.verify(truncated_pwd, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Generates a secure salt and hashes the password using bcrypt.
    """
    truncated_pwd = password[:72]
    return pwd_context.hash(truncated_pwd)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.
    Uses timezone-aware datetime objects for token expiration (OWASP best practice).
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject)
    }
    
    # Sign token using JWT secret key and algorithm from configurations
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> Optional[int]:
    """
    Validates and decodes a JWT access token.
    Returns the user ID (sub claim) as an integer if valid, else returns None.
    Raises no exceptions to prevent leakage of internal signature validation details.
    """
    try:
        # Decodes token verifying signature and expiration time claims
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            logger.debug("Token payload missing sub claim")
            return None
        return int(user_id_str)
    except ExpiredSignatureError:
        logger.debug("Token signature has expired")
        return None
    except JWTClaimsError:
        logger.debug("Token claims validation failed")
        return None
    except JWTError as e:
        logger.debug(f"Token signature validation failed: {str(e)}")
        return None
    except ValueError as e:
        logger.debug(f"Invalid token format: {str(e)}")
        return None

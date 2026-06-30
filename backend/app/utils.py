from fastapi import HTTPException, status
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.config import settings
import secrets
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_join_code(length: int = None) -> str:
        """Generate a random alphanumeric join code"""
        length = length or settings.JOIN_CODE_LENGTH
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    @staticmethod
    def generate_device_token() -> str:
        """Generate a secure device token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def get_join_code_expiration() -> datetime:
        """Get join code expiration time"""
        return datetime.utcnow() + timedelta(hours=settings.JOIN_CODE_EXPIRATION_HOURS)

class ErrorResponses:
    INVALID_CREDENTIALS = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )
    
    UNAUTHORIZED = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )
    
    FORBIDDEN = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to access this resource"
    )
    
    NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resource not found"
    )
    
    INVALID_JOIN_CODE = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired join code"
    )
    
    INVALID_EVENT = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid event"
    )
    
    DEVICE_REVOKED = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Device has been revoked"
    )

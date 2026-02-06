"""
Security utilities for password hashing and JWT token management.
"""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.utils.config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Args:
        password: Plain-text password to hash

    Returns:
        Hashed password string

    Example:
        >>> hashed = hash_password("my_secret_password")
        >>> print(hashed)
        $2b$12$...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a hashed password.
    """
    try:
        # Try using bcrypt directly to avoid passlib/bcrypt 4.0+ issues
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception:
        # Fallback to passlib if direct bcrypt fails
        return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of claims to encode in the token (e.g., {"sub": "user@example.com"})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        Dictionary of claims if token is valid, None otherwise

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> payload = decode_access_token(token)
        >>> print(payload["sub"])
        user@example.com
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None

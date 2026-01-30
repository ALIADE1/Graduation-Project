"""
FastAPI dependencies for authentication and authorization.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from src.db.database import get_session
from src.db.models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.security import decode_access_token

# OAuth2 scheme for extracting bearer tokens from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
) -> User:
    """
    Get the currently authenticated user from JWT token.

    This dependency extracts the JWT token from the Authorization header,
    validates it, and retrieves the corresponding user from the database.

    Args:
        token: JWT token from Authorization header
        session: Database session

    Returns:
        User object if authentication is successful

    Raises:
        HTTPException: 401 Unauthorized if token is invalid or user not found

    Usage:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello {current_user.username}"}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Extract user identity from token (sub is username in auth_routes.py)
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception

    # Retrieve user from database
    statement = select(User).where(User.username == username)
    result = await session.exec(statement)
    user = result.first()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user (for future soft-delete support).

    Currently returns the user as-is, but can be extended to check
    for account status, email verification, banned users, etc.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User object if user is active

    Raises:
        HTTPException: 400 Bad Request if user is inactive

    Usage:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_active_user)):
            return {"message": f"Hello active user {user.username}"}
    """
    # Future: Check if user.is_active, user.is_verified, etc.
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")

    return current_user

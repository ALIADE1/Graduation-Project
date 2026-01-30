"""
Authentication API endpoints for user signup and login.
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.database import get_session
from src.db.models import User
from src.auth.security import hash_password, verify_password, create_access_token
from src.utils.logger import setup_logger
from src.utils.config import settings

logger = setup_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request/Response Models
class SignupRequest(BaseModel):
    """Request model for user signup."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    age: Optional[int] = Field(None, ge=0, le=120, description="User age")
    gender: Optional[str] = Field(None, max_length=20, description="User gender")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "username": "Student123",
                "password": "secure_password",
            }
        }


class UserResponse(BaseModel):
    """Response model for user data (without password)."""

    id: int
    email: str
    username: str
    role: str
    age: Optional[int] = None
    gender: Optional[str] = None
    created_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "student@example.com",
                "username": "Student123",
                "role": "user",
                "created_at": "2024-01-27T05:00:00",
            }
        }


class TokenResponse(BaseModel):
    """Response model for login token."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in minutes")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 60,
            }
        }


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    signup_data: SignupRequest, session: AsyncSession = Depends(get_session)
):
    """
    Register a new user.
    """
    # Check if email or username already exists
    statement = select(User).where(
        (User.email == signup_data.email) | (User.username == signup_data.username)
    )
    result = await session.exec(statement)
    existing_user = result.first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or Username already registered",
        )

    # Create new user with hashed password
    hashed_password_value = hash_password(signup_data.password)

    new_user = User(
        email=signup_data.email,
        username=signup_data.username,
        password_hash=hashed_password_value,
        role="user",
        age=signup_data.age,
        gender=signup_data.gender,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    logger.info(f"New user registered: {new_user.email}")

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        role=new_user.role,
        age=new_user.age,
        gender=new_user.gender,
        created_at=str(new_user.created_at),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """
    Authenticate user and return JWT access token.
    """
    # Find user by username
    statement = select(User).where(User.username == form_data.username)
    result = await session.exec(statement)
    user = result.first()

    # If not found by username, try finding by email
    if not user:
        statement = select(User).where(User.email == form_data.username)
        result = await session.exec(statement)
        user = result.first()

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    logger.info(f"User logged in: {user.username}")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes,
    )

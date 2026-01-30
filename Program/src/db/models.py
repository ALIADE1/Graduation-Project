"""
SQLModel database models for PostgreSQL (Supabase).
Optimized for cloud deployment and mobile app integration.
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255, nullable=False)
    username: str = Field(max_length=100, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    role: str = Field(default="user", max_length=50, nullable=False)
    age: Optional[int] = Field(default=None)
    gender: Optional[str] = Field(default=None, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    notes: List["Note"] = Relationship(back_populates="owner")


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100, nullable=False)
    description: Optional[str] = Field(default=None, max_length=500)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Note(SQLModel, table=True):
    """
    Note model synchronized with Supabase schema.
    Removed content_json and keywords to prevent UndefinedColumnError.
    """

    __tablename__ = "notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)
    video_url: str = Field(index=True, max_length=500, nullable=False)
    video_title: str = Field(max_length=500, nullable=False)
    summary_content: str = Field(nullable=False)
    category: Optional[str] = Field(default="Uncategorized", max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    owner: Optional[User] = Relationship(back_populates="notes")

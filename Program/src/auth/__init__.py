"""
Authentication module for YouTube Study Notes AI.
Provides secure password hashing and JWT token management.
"""

from .security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from .dependencies import (
    get_current_user,
    get_current_active_user,
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "get_current_active_user",
]

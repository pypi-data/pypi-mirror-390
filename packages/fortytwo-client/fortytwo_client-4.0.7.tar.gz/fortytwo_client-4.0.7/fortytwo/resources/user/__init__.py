"""
User resource for the FortyTwo API.

This module provides the User model and UserManager for interacting
with user data.
"""

from fortytwo.resources.user.manager import UserManager
from fortytwo.resources.user.user import User, UserImage


__all__ = [
    "User",
    "UserImage",
    "UserManager",
]

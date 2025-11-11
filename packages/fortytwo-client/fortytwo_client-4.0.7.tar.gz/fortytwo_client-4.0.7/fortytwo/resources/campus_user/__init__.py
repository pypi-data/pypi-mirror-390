"""
Campus User resource for the FortyTwo API.

This module provides the CampusUser model and CampusUserManager for interacting
with campus user data.
"""

from fortytwo.resources.campus_user.campus_user import CampusUser
from fortytwo.resources.campus_user.manager import CampusUserManager


__all__ = [
    "CampusUser",
    "CampusUserManager",
]

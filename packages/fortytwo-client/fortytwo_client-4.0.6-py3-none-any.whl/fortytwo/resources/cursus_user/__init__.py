"""
Cursus User resource for the FortyTwo API.

This module provides the CursusUser model and CursusUserManager for interacting
with cursus user data.
"""

from fortytwo.resources.cursus_user.cursus_user import CursusUser
from fortytwo.resources.cursus_user.manager import CursusUserManager


__all__ = [
    "CursusUser",
    "CursusUserManager",
]

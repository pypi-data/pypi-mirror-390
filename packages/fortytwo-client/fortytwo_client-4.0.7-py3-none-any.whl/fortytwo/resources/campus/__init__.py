"""
Campus resource for the FortyTwo API.

This module provides the Campus model and CampusManager for interacting
with campus data.
"""

from fortytwo.resources.campus.campus import Campus
from fortytwo.resources.campus.manager import CampusManager


__all__ = [
    "Campus",
    "CampusManager",
]

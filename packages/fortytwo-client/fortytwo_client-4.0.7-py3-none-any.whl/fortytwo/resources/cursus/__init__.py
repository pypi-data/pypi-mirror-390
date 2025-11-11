"""
Cursus resource for the FortyTwo API.

This module provides the Cursus model and CursusManager for interacting
with cursus data.
"""

from fortytwo.resources.cursus.cursus import Cursus
from fortytwo.resources.cursus.manager import CursusManager


__all__ = [
    "Cursus",
    "CursusManager",
]

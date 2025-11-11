"""
Location resource for the FortyTwo API.

This module provides the Location model and LocationManager for interacting
with location data.
"""

from fortytwo.resources.location.location import Location
from fortytwo.resources.location.manager import LocationManager


__all__ = [
    "Location",
    "LocationManager",
]

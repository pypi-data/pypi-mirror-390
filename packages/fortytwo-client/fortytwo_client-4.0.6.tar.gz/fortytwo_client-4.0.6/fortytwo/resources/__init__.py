"""
This module provides a base class for 42 API resources.
"""

from fortytwo.resources import (
    campus,
    cursus,
    cursus_user,
    custom,
    location,
    project,
    project_user,
    team,
    token,
    user,
)
from fortytwo.resources.model import Model


__all__ = [
    "Model",
    "campus",
    "cursus",
    "cursus_user",
    "custom",
    "location",
    "project",
    "project_user",
    "team",
    "token",
    "user",
]

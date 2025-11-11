"""
ProjectUser resource for the FortyTwo API.

This module provides the ProjectUser model and ProjectUserManager for interacting
with project-user relationship data.
"""

from fortytwo.resources.project_user.manager import ProjectUserManager
from fortytwo.resources.project_user.project_user import ProjectUser


__all__ = [
    "ProjectUser",
    "ProjectUserManager",
]

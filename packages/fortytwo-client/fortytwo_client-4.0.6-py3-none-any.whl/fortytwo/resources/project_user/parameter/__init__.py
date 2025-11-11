"""
ProjectUser-specific query parameters for the FortyTwo API.

This module provides a namespace class for project_user filtering and range parameters.
"""

from fortytwo.resources.project_user.parameter.filter import ProjectUserFilter
from fortytwo.resources.project_user.parameter.parameter import (
    ProjectUserParameter,
)
from fortytwo.resources.project_user.parameter.range import ProjectUserRange


class ProjectUserParameters:
    """
    Namespace for project_user-specific query parameters.
    """

    Filter = ProjectUserFilter
    Range = ProjectUserRange
    Parameter = ProjectUserParameter


__all__ = ["ProjectUserParameters"]

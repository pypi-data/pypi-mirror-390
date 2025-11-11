"""
Project-specific query parameters for the FortyTwo API.

This module provides a namespace class for project filtering, sorting, and range parameters.
"""

from fortytwo.resources.project.parameter.filter import ProjectFilter
from fortytwo.resources.project.parameter.parameter import ProjectParameter
from fortytwo.resources.project.parameter.range import ProjectRange
from fortytwo.resources.project.parameter.sort import ProjectSort


class ProjectParameters:
    """
    Namespace for project-specific query parameters.
    """

    Filter = ProjectFilter
    Sort = ProjectSort
    Range = ProjectRange
    Parameter = ProjectParameter


__all__ = ["ProjectParameters"]

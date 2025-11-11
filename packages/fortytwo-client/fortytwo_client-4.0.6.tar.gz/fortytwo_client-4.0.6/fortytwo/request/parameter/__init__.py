"""
Query parameter utilities for the FortyTwo API client.

This module provides base parameter classes and resource-specific parameter namespaces.
"""

from fortytwo.request.parameter.parameter import (
    Filter,
    PageNumber,
    PageSize,
    Parameter,
    Range,
    Sort,
    SortDirection,
)
from fortytwo.resources.campus.parameter import CampusParameters
from fortytwo.resources.cursus.parameter import CursusParameters
from fortytwo.resources.cursus_user.parameter import CursusUserParameters
from fortytwo.resources.location.parameter import LocationParameters
from fortytwo.resources.project.parameter import ProjectParameters
from fortytwo.resources.project_user.parameter import ProjectUserParameters
from fortytwo.resources.team.parameter import TeamParameters
from fortytwo.resources.user.parameter import UserParameters


__all__ = [
    "CampusParameters",
    "CursusParameters",
    "CursusUserParameters",
    "Filter",
    "LocationParameters",
    "PageNumber",
    "PageSize",
    "Parameter",
    "ProjectParameters",
    "ProjectUserParameters",
    "Range",
    "Sort",
    "SortDirection",
    "TeamParameters",
    "UserParameters",
]

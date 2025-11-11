"""
Campus User-specific query parameters for the FortyTwo API.

This module provides a namespace class for campus user filtering, sorting, and range parameters.
"""

from fortytwo.resources.campus_user.parameter.filter import CampusUserFilter
from fortytwo.resources.campus_user.parameter.parameter import CampusUserParameter
from fortytwo.resources.campus_user.parameter.range import CampusUserRange
from fortytwo.resources.campus_user.parameter.sort import CampusUserSort


class CampusUserParameters:
    """
    Namespace for campus user-specific query parameters.
    """

    Filter = CampusUserFilter
    Sort = CampusUserSort
    Range = CampusUserRange
    Parameter = CampusUserParameter


__all__ = ["CampusUserParameters"]

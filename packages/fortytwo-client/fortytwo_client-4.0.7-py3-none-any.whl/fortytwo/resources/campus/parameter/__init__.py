"""
Campus-specific query parameters for the FortyTwo API.

This module provides a namespace class for campus filtering, sorting, and range parameters.
"""

from fortytwo.resources.campus.parameter.filter import CampusFilter
from fortytwo.resources.campus.parameter.range import CampusRange
from fortytwo.resources.campus.parameter.sort import CampusSort


class CampusParameters:
    """
    Namespace for campus-specific query parameters.
    """

    Filter = CampusFilter
    Sort = CampusSort
    Range = CampusRange


__all__ = ["CampusParameters"]

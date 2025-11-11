"""
Cursus User-specific query parameters for the FortyTwo API.

This module provides a namespace class for cursus user filtering, sorting, and range parameters.
"""

from fortytwo.resources.cursus_user.parameter.filter import CursusUserFilter
from fortytwo.resources.cursus_user.parameter.parameter import CursusUserParameter
from fortytwo.resources.cursus_user.parameter.range import CursusUserRange
from fortytwo.resources.cursus_user.parameter.sort import CursusUserSort


class CursusUserParameters:
    """
    Namespace for cursus user-specific query parameters.
    """

    Filter = CursusUserFilter
    Sort = CursusUserSort
    Range = CursusUserRange
    Parameter = CursusUserParameter


__all__ = ["CursusUserParameters"]

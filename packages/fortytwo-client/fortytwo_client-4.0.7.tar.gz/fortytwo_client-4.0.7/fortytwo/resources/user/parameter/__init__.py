"""
User-specific query parameters for the FortyTwo API.

This module provides a namespace class for user filtering, sorting, and range parameters.
"""

from fortytwo.resources.user.parameter.filter import UserFilter
from fortytwo.resources.user.parameter.parameter import UserParameter
from fortytwo.resources.user.parameter.range import UserRange
from fortytwo.resources.user.parameter.sort import UserSort


class UserParameters:
    """
    Namespace for user-specific query parameters.
    """

    Filter = UserFilter
    Sort = UserSort
    Range = UserRange
    Parameter = UserParameter


__all__ = ["UserParameters"]

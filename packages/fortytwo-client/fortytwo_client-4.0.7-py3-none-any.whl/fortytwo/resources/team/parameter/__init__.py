"""
Team-specific query parameters for the FortyTwo API.

This module provides a namespace class for team filtering, sorting, and range parameters.
"""

from fortytwo.resources.team.parameter.filter import TeamFilter
from fortytwo.resources.team.parameter.parameter import TeamParameter
from fortytwo.resources.team.parameter.range import TeamRange
from fortytwo.resources.team.parameter.sort import TeamSort


class TeamParameters:
    """
    Namespace for team-specific query parameters.
    """

    Filter = TeamFilter
    Sort = TeamSort
    Range = TeamRange
    Parameter = TeamParameter


__all__ = ["TeamParameters"]

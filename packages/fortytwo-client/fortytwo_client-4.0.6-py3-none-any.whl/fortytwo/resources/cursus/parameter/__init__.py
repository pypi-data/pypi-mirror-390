"""
Cursus-specific query parameters for the FortyTwo API.

This module provides a namespace class for cursus filtering, sorting, and range parameters.
"""

from fortytwo.resources.cursus.parameter.filter import CursusFilter
from fortytwo.resources.cursus.parameter.range import CursusRange
from fortytwo.resources.cursus.parameter.sort import CursusSort


class CursusParameters:
    """
    Namespace for cursus-specific query parameters.
    """

    Filter = CursusFilter
    Sort = CursusSort
    Range = CursusRange


__all__ = ["CursusParameters"]

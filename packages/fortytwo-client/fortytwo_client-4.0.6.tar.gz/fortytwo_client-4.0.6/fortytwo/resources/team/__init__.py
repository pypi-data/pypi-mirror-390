"""
Team resource for the FortyTwo API.

This module provides the Team and TeamUser models and TeamManager for interacting
with team data.
"""

from fortytwo.resources.team.manager import TeamManager
from fortytwo.resources.team.team import Team, TeamUser


__all__ = [
    "Team",
    "TeamManager",
    "TeamUser",
]

"""
This module provides resources for getting project users from the 42 API.
"""

from typing import TYPE_CHECKING, Any, Self

from dateutil.parser import parse as parse_date

from fortytwo.json import register_serializer
from fortytwo.resources.model import Model


if TYPE_CHECKING:
    from datetime import datetime


class ProjectUser(Model):
    """
    This class provides a representation of a 42 project user.
    """

    def __init__(self: Self, data: Any) -> None:
        from fortytwo.resources.project.project import ProjectReference
        from fortytwo.resources.team.team import Team
        from fortytwo.resources.user.user import User

        # fmt: off
        self.id: int                        = data["id"]
        self.occurrence: int                = data["occurrence"]
        self.final_mark: int | None         = data["final_mark"]
        self.status: str                    = data["status"]
        self.validated: bool | None         = data["validated?"]
        self.current_team_id: int           = data["current_team_id"]

        self.project: ProjectReference      = ProjectReference(data["project"])
        self.user: User | None              = User(data.get("user")) if data.get("user") is not None else None
        self.teams: list[Team]              = [Team(t) for t in data.get("teams", [])]
        self.cursus_ids: list[int]          = data["cursus_ids"]

        self.marked_at: datetime | None     = parse_date(data["marked_at"]) if data["marked_at"] else None
        self.marked: bool                   = data["marked"]
        self.retriable_at: datetime | None  = parse_date(data["retriable_at"]) if data["retriable_at"] else None
        self.created_at: datetime           = parse_date(data["created_at"])
        self.updated_at: datetime           = parse_date(data["updated_at"])
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<ProjectUser {self.user.login if self.user else 'Unknown'} - {self.project.name}>"

    def __str__(self: Self) -> str:
        return f"{self.user.login if self.user else 'Unknown'} - {self.project.name}"


# fmt: off
register_serializer(
    ProjectUser,
    lambda p: {
        "id":               p.id,
        "occurrence":       p.occurrence,
        "final_mark":       p.final_mark,
        "status":           p.status,
        "validated":        p.validated,
        "current_team_id":  p.current_team_id,
        "project":          p.project,
        "user":             p.user,
        "teams":            p.teams,
        "cursus_ids":       p.cursus_ids,
        "marked_at":        p.marked_at.isoformat() if p.marked_at else None,
        "marked":           p.marked,
        "retriable_at":     p.retriable_at.isoformat() if p.retriable_at else None,
        "created_at":       p.created_at.isoformat(),
        "updated_at":       p.updated_at.isoformat(),
    },
)
# fmt: on

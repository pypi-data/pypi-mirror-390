"""
This module provides resources for team data from the 42 API.
"""

from typing import TYPE_CHECKING, Any, Self

from dateutil.parser import parse as parse_date

from fortytwo.json import register_serializer
from fortytwo.resources.model import Model


if TYPE_CHECKING:
    from datetime import datetime


class TeamUser(Model):
    """
    Lightweight representation of a user within a team.
    """

    def __init__(self: Self, data: Any) -> None:
        # fmt: off
        self.id: int                    = data["id"]
        self.login: str                 = data["login"]
        self.url: str                   = data["url"]
        self.leader: bool               = data["leader"]
        self.occurrence: int            = data["occurrence"]
        self.validated: bool            = data["validated"]
        self.projects_user_id: int      = data["projects_user_id"]
        # fmt: on

    def __repr__(self: Self) -> str:
        leader_badge = " (leader)" if self.leader else ""
        return f"<TeamUser {self.login}{leader_badge}>"

    def __str__(self: Self) -> str:
        return self.login


class Team(Model):
    """
    This class provides a representation of a 42 team.
    """

    def __init__(self: Self, data: Any) -> None:
        # fmt: off
        self.id: int                            = data["id"]
        self.name: str                          = data["name"]
        self.url: str                           = data["url"]
        self.final_mark: int | None             = data["final_mark"]
        self.project_id: int                    = data["project_id"]

        self.created_at: datetime               = parse_date(data["created_at"])
        self.updated_at: datetime               = parse_date(data["updated_at"])

        self.status: str                        = data["status"]
        self.terminating_at: datetime | None    = parse_date(data["terminating_at"]) if data["terminating_at"] else None

        self.users: list[TeamUser]              = [TeamUser(u) for u in data["users"]]

        self.locked: bool                       = data["locked?"]
        self.validated: bool | None             = data["validated?"]
        self.closed: bool                       = data["closed?"]

        self.repo_url: str | None               = data["repo_url"]
        self.repo_uuid: str                     = data["repo_uuid"]

        self.locked_at: datetime | None         = parse_date(data["locked_at"]) if data["locked_at"] else None
        self.closed_at: datetime | None         = parse_date(data["closed_at"]) if data["closed_at"] else None

        self.project_session_id: int            = data["project_session_id"]
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<Team {self.name}>"

    def __str__(self: Self) -> str:
        return self.name


# fmt: off
register_serializer(
    TeamUser,
    lambda tu: {
        "id":                   tu.id,
        "login":                tu.login,
        "url":                  tu.url,
        "leader":               tu.leader,
        "occurrence":           tu.occurrence,
        "validated":            tu.validated,
        "projects_user_id":     tu.projects_user_id,
    },
)
# fmt: on

# fmt: off
register_serializer(
    Team,
    lambda t: {
        "id":                   t.id,
        "name":                 t.name,
        "url":                  t.url,
        "final_mark":           t.final_mark,
        "project_id":           t.project_id,
        "created_at":           t.created_at.isoformat(),
        "updated_at":           t.updated_at.isoformat(),
        "status":               t.status,
        "terminating_at":       t.terminating_at.isoformat() if t.terminating_at else None,
        "users":                t.users,
        "locked":               t.locked,
        "validated":            t.validated,
        "closed":               t.closed,
        "repo_url":             t.repo_url,
        "repo_uuid":            t.repo_uuid,
        "locked_at":            t.locked_at.isoformat() if t.locked_at else None,
        "closed_at":            t.closed_at.isoformat() if t.closed_at else None,
        "project_session_id":   t.project_session_id,
    },
)
# fmt: on

"""
This module provides resources for cursus user data from the 42 API.
"""

from typing import TYPE_CHECKING, Any, Self

from dateutil.parser import parse as parse_date

from fortytwo.json import register_serializer
from fortytwo.resources.model import Model


if TYPE_CHECKING:
    from datetime import datetime


class CursusUser(Model):
    """
    This class provides a representation of a 42 cursus user.
    Represents a user's enrollment and progress in a specific cursus.
    """

    def __init__(self: Self, data: Any) -> None:
        from fortytwo.resources.cursus import Cursus
        from fortytwo.resources.user import User

        # fmt: off
        self.id: int                        = data["id"]
        self.begin_at: datetime             = parse_date(data["begin_at"])
        self.end_at: datetime | None        = parse_date(data["end_at"]) if data["end_at"] else None
        self.grade: str | None              = data["grade"]
        self.level: float                   = data["level"]
        self.cursus_id: int                 = data["cursus_id"]
        self.has_coalition: bool            = data["has_coalition"]

        self.blackholed_at: datetime | None = parse_date(data["blackholed_at"]) if data["blackholed_at"] else None
        self.created_at: datetime           = parse_date(data["created_at"])
        self.updated_at: datetime           = parse_date(data["updated_at"])

        self.user: User                     = User(data["user"])
        self.cursus: Cursus                 = Cursus(data["cursus"])
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<CursusUser {self.user.login} in {self.cursus.name}>"

    def __str__(self: Self) -> str:
        return f"{self.user.login} - {self.cursus.name}"


# fmt: off
register_serializer(
    CursusUser,
    lambda cu: {
        "id":               cu.id,
        "begin_at":         cu.begin_at.isoformat(),
        "end_at":           cu.end_at.isoformat() if cu.end_at else None,
        "grade":            cu.grade,
        "level":            cu.level,
        "cursus_id":        cu.cursus_id,
        "has_coalition":    cu.has_coalition,
        "blackholed_at":    cu.blackholed_at.isoformat() if cu.blackholed_at else None,
        "created_at":       cu.created_at.isoformat(),
        "updated_at":       cu.updated_at.isoformat(),
        "user":             cu.user,
        "cursus":           cu.cursus,
    },
)
# fmt: on

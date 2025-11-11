"""
This module provides resources for location of users from the 42 API.
"""

from typing import TYPE_CHECKING, Any, Self

from dateutil.parser import parse as parse_date

from fortytwo.json import register_serializer
from fortytwo.resources.model import Model


if TYPE_CHECKING:
    from datetime import datetime


class Location(Model):
    """
    This class provides a representation of a 42 location.

    Represents a location/session record tracking when and where
    a user logged into a campus workstation.
    """

    def __init__(self: Self, data: Any) -> None:
        from fortytwo.resources.user.user import User

        # fmt: off
        self.id: int                    = data["id"]
        self.begin_at: datetime         = parse_date(data["begin_at"])
        self.end_at: datetime | None    = parse_date(data["end_at"]) if data["end_at"] else None
        self.primary: bool              = data["primary"]
        self.floor: str | None          = data.get("floor")
        self.row: str | None            = data.get("row")
        self.post: str | None           = data.get("post")
        self.host: str                  = data["host"]
        self.campus_id: int             = data["campus_id"]

        self.user: User                 = User(data["user"])
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<Location {self.id}>"

    def __str__(self: Self) -> str:
        return str(self.id)


# fmt: off
register_serializer(
    Location,
    lambda loc: {
        "id":           loc.id,
        "begin_at":     loc.begin_at.isoformat(),
        "end_at":       loc.end_at.isoformat() if loc.end_at else None,
        "primary":      loc.primary,
        "floor":        loc.floor,
        "row":          loc.row,
        "post":         loc.post,
        "host":         loc.host,
        "campus_id":    loc.campus_id,
        "user":         loc.user,
    },
)
# fmt: on

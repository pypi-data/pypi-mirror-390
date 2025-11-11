"""
This module provides resources for campus user data from the 42 API.
"""

from typing import TYPE_CHECKING, Any, Self

from dateutil.parser import parse as parse_date

from fortytwo.json import register_serializer
from fortytwo.resources.model import Model


if TYPE_CHECKING:
    from datetime import datetime


class CampusUser(Model):
    """
    This class provides a representation of a 42 campus user.
    Represents a user's association with a specific campus.
    """

    def __init__(self: Self, data: Any) -> None:
        # fmt: off
        self.id: int                = data["id"]
        self.user_id: int           = data["user_id"]
        self.campus_id: int         = data["campus_id"]
        self.is_primary: bool       = data["is_primary"]
        self.created_at: datetime   = parse_date(data["created_at"])
        self.updated_at: datetime   = parse_date(data["updated_at"])
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<CampusUser {self.user_id} at campus {self.campus_id}>"

    def __str__(self: Self) -> str:
        primary_status = "primary" if self.is_primary else "secondary"
        return f"User {self.user_id} - Campus {self.campus_id} ({primary_status})"


# fmt: off
register_serializer(
    CampusUser,
    lambda cu: {
        "id":           cu.id,
        "user_id":      cu.user_id,
        "campus_id":    cu.campus_id,
        "is_primary":   cu.is_primary,
        "created_at":   cu.created_at.isoformat(),
        "updated_at":   cu.updated_at.isoformat(),
    },
)
# fmt: on

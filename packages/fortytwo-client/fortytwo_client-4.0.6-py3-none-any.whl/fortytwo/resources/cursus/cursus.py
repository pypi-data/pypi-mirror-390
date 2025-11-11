"""
This module provides resources for cursus data from the 42 API.
"""

from typing import Any, Self

from fortytwo.json import register_serializer
from fortytwo.resources.model import Model


class Cursus(Model):
    """
    This class provides a representation of a 42 cursus.
    """

    def __init__(self: Self, data: Any) -> None:
        # fmt: off
        self.id: int            = data["id"]
        self.created_at: str    = data["created_at"]
        self.name: str          = data["name"]
        self.slug: str          = data["slug"]
        self.kind: str          = data["kind"]
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<Cursus {self.name}>"

    def __str__(self: Self) -> str:
        return self.name


# fmt: off
register_serializer(
    Cursus,
    lambda c: {
        "id":           c.id,
        "created_at":   c.created_at,
        "name":         c.name,
        "slug":         c.slug,
        "kind":         c.kind,
    },
)
# fmt: on

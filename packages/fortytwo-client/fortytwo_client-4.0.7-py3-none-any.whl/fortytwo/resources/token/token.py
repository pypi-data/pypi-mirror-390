"""
This module provides resources for getting token information.
"""

from typing import Any, Self

from fortytwo.json import register_serializer
from fortytwo.resources.model import Model


class Token(Model):
    """
    This class provides a representation of a token
    """

    def __init__(self: Self, data: Any) -> None:
        # fmt: off
        self.owner: int | None      = data["resource_owner_id"]
        self.scopes: list[str]      = data["scopes"]

        self.expires: int           = data["expires_in_seconds"]
        self.uid: str               = data["application"]["uid"]
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<Token {self.uid}>"

    def __str__(self: Self) -> str:
        return self.uid


# fmt: off
register_serializer(
    Token,
    lambda p: {
        "owner":    p.owner,
        "scopes":   p.scopes,
        "expires":  p.expires,
        "uid":      p.uid,
    },
)
# fmt: on

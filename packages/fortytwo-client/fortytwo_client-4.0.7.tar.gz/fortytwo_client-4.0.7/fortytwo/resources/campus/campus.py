"""
This module provides resources for campus data from the 42 API.
"""

from typing import Any, Self

from fortytwo.json import register_serializer
from fortytwo.resources.model import Model


class Campus(Model):
    """
    This class provides a representation of a 42 campus.
    """

    def __init__(self: Self, data: Any) -> None:
        # fmt: off
        self.id: int                        = data["id"]
        self.name: str                      = data["name"]
        self.time_zone: str                 = data["time_zone"]

        # TODO: Create a Language resource
        self.language: dict[str, Any] = {
            "id":                           data["language"]["id"],
            "name":                         data["language"]["name"],
            "identifier":                   data["language"]["identifier"],
        }

        self.users_count: int               = data["users_count"]
        self.vogsphere_id: int              = data["vogsphere_id"]

        self.country: str                   = data["country"]
        self.address: str                   = data["address"]
        self.zip: str                       = data["zip"]
        self.city: str                      = data["city"]

        self.website: str                   = data["website"]
        self.facebook: str                  = data["facebook"]
        self.twitter: str                   = data["twitter"]

        self.active: bool                   = data["active"]
        self.public: bool                   = data["public"]
        self.email_extension: str           = data["email_extension"]
        self.default_hidden_phone: bool     = data["default_hidden_phone"]
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<Campus {self.name}>"

    def __str__(self: Self) -> str:
        return self.name


# fmt: off
register_serializer(
    Campus,
    lambda campus: {
        "id":                       campus.id,
        "name":                     campus.name,
        "time_zone":                campus.time_zone,
        "language":                 campus.language,
        "users_count":              campus.users_count,
        "vogsphere_id":             campus.vogsphere_id,
        "country":                  campus.country,
        "address":                  campus.address,
        "zip":                      campus.zip,
        "city":                     campus.city,
        "website":                  campus.website,
        "facebook":                 campus.facebook,
        "twitter":                  campus.twitter,
        "active":                   campus.active,
        "public":                   campus.public,
        "email_extension":          campus.email_extension,
        "default_hidden_phone":     campus.default_hidden_phone,
    },
)
# fmt: on

"""
This module provides resources for getting users from the 42 API.
"""

from typing import TYPE_CHECKING, Any, Self

from dateutil.parser import parse as parse_date

from fortytwo.json import register_serializer
from fortytwo.resources.model import Model


if TYPE_CHECKING:
    from datetime import datetime


class UserImage:
    """
    Represents a user's profile image with different versions.
    """

    def __init__(self: Self, data: dict[str, Any]) -> None:
        # fmt: off
        self.link: str      = data["link"]

        self.large: str     = data["versions"]["large"]
        self.medium: str    = data["versions"]["medium"]
        self.small: str     = data["versions"]["small"]
        self.micro: str     = data["versions"]["micro"]
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<UserImage {self.link}>"

    def __str__(self: Self) -> str:
        return self.link


class User(Model):
    """
    This class provides a representation of a 42 user.
    """

    def __init__(self: Self, data: Any) -> None:
        from fortytwo.resources.campus.campus import Campus
        from fortytwo.resources.campus_user.campus_user import CampusUser
        from fortytwo.resources.cursus_user.cursus_user import CursusUser
        from fortytwo.resources.project_user.project_user import ProjectUser

        # fmt: off
        self.id: int                            = data["id"]
        self.email: str                         = data["email"]
        self.login: str                         = data["login"]
        self.first_name: str                    = data["first_name"]
        self.last_name: str                     = data["last_name"]
        self.usual_full_name: str               = data["usual_full_name"]
        self.usual_first_name: str | None       = data.get("usual_first_name")
        self.url: str                           = data["url"]
        self.phone: str                         = data["phone"]
        self.displayname: str                   = data["displayname"]

        self.kind: str                          = data["kind"]
        self.image: UserImage                   = UserImage(data["image"])
        self.staff: bool                        = data["staff?"]
        self.correction_point: int              = data["correction_point"]
        self.pool_month: str                    = data["pool_month"]
        self.pool_year: str                     = data["pool_year"]
        self.location: str | None               = data.get("location")
        self.wallet: int                        = data["wallet"]


        self.anonymize_date: datetime | None    = parse_date(data["anonymize_date"]) if data.get("anonymize_date") else None
        self.data_erasure_date: datetime | None = parse_date(data["data_erasure_date"]) if data.get("data_erasure_date") else None
        self.created_at: datetime               = parse_date(data["created_at"])
        self.updated_at: datetime               = parse_date(data["updated_at"])
        self.alumnized_at: datetime | None      = parse_date(data["alumnized_at"]) if data.get("alumnized_at") else None

        self.alumni: bool                       = data["alumni?"]
        self.active: bool                       = data["active?"]

        self.projects_users: list               = [ProjectUser(pu) for pu in data.get("projects_users", [])]
        self.cursus_users: list                 = [CursusUser(cu) for cu in data.get("cursus_users", [])]
        self.campus: list                       = [Campus(ca) for ca in data.get("campus", [])]
        self.campus_users: list                 = [CampusUser(cu) for cu in data.get("campus_users", [])]
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<User {self.login}>"

    def __str__(self: Self) -> str:
        return self.login


# fmt: off
register_serializer(
    UserImage,
    lambda img: {
        "link":                 img.link,
        "large":                img.large,
        "medium":               img.medium,
        "small":                img.small,
        "micro":                img.micro,
    },
)
# fmt: on

# fmt: off
register_serializer(
    User,
    lambda u: {
        "id":                   u.id,
        "email":                u.email,
        "login":                u.login,
        "first_name":           u.first_name,
        "last_name":            u.last_name,
        "usual_full_name":      u.usual_full_name,
        "usual_first_name":     u.usual_first_name,
        "url":                  u.url,
        "phone":                u.phone,
        "displayname":          u.displayname,
        "kind":                 u.kind,
        "image":                u.image,
        "staff":                u.staff,
        "correction_point":     u.correction_point,
        "pool_month":           u.pool_month,
        "pool_year":            u.pool_year,
        "location":             u.location,
        "wallet":               u.wallet,
        "anonymize_date":       u.anonymize_date.isoformat() if u.anonymize_date else None,
        "data_erasure_date":    u.data_erasure_date.isoformat() if u.data_erasure_date else None,
        "created_at":           u.created_at.isoformat(),
        "updated_at":           u.updated_at.isoformat(),
        "alumnized_at":         u.alumnized_at.isoformat() if u.alumnized_at else None,
        "alumni":               u.alumni,
        "active":               u.active,
        "cursus_users":         u.cursus_users,
        "projects_users":       u.projects_users,
        "campus":               u.campus,
        "campus_users":         u.campus_users,
    },
)
# fmt: on

"""
This module provides resources for getting projects from the 42 API.
"""

from typing import TYPE_CHECKING, Any, Self

from dateutil.parser import parse as parse_date

from fortytwo.json import register_serializer
from fortytwo.resources.model import Model


if TYPE_CHECKING:
    from datetime import datetime


class ProjectReference(Model):
    """
    Lightweight representation of a project reference (used in parent/children).
    Contains only basic project identification fields.
    """

    def __init__(self: Self, data: Any) -> None:
        # fmt: off
        self.id: int        = data["id"]
        self.name: str      = data["name"]
        self.slug: str      = data["slug"]
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<ProjectReference {self.name}>"

    def __str__(self: Self) -> str:
        return self.name


class Project(Model):
    """
    This class provides a representation of a 42 project.
    """

    def __init__(self: Self, data: Any) -> None:
        from fortytwo.resources.campus.campus import Campus
        from fortytwo.resources.cursus.cursus import Cursus

        # fmt: off
        self.id: int                            = data["id"]
        self.name: str                          = data["name"]
        self.slug: str                          = data["slug"]
        self.difficulty: int                    = data["difficulty"]
        self.created_at: datetime               = parse_date(data["created_at"])
        self.updated_at: datetime               = parse_date(data["updated_at"])
        self.exam: bool                         = data["exam"]

        self.parent: ProjectReference | None    = ProjectReference(data["parent"]) if data["parent"] else None
        self.children: list[ProjectReference]   = [ProjectReference(c) for c in data["children"]]
        self.cursus: list[Cursus]               = [Cursus(c) for c in data["cursus"]]
        self.campus: list[Campus]               = [Campus(c) for c in data["campus"]]
        # fmt: on

    def __repr__(self: Self) -> str:
        return f"<Project {self.name}>"

    def __str__(self: Self) -> str:
        return self.name


# fmt: off
register_serializer(
    ProjectReference,
    lambda pr: {
        "id":           pr.id,
        "name":         pr.name,
        "slug":         pr.slug,
    },
)
# fmt: on

# fmt: off
register_serializer(
    Project,
    lambda p: {
        "id":           p.id,
        "name":         p.name,
        "slug":         p.slug,
        "difficulty":   p.difficulty,
        "created_at":   p.created_at.isoformat(),
        "updated_at":   p.updated_at.isoformat(),
        "exam":         p.exam,
        "parent":       p.parent,
        "children":     p.children,
        "cursus":       p.cursus,
        "campus":       p.campus,
    },
)
# fmt: on

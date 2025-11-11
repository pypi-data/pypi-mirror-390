from __future__ import annotations

from typing import TYPE_CHECKING

from fortytwo.request.parameter.pagination import with_pagination
from fortytwo.resources.project.resource import (
    GetProjects,
    GetProjectsByCursusId,
    GetProjectsById,
    GetProjectsByProjectId,
)


if TYPE_CHECKING:
    from fortytwo.client import Client
    from fortytwo.request.parameter import Parameter
    from fortytwo.resources.project.project import Project


class ProjectManager:
    """
    Manager for project-related API operations.
    """

    def __init__(self, client: Client) -> None:
        self._client = client

    @with_pagination
    def get_all(
        self,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Project]:
        """
        Get all projects.

        Args:
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Project objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetProjects(), *params)

    @with_pagination
    def get_by_cursus_id(
        self,
        cursus_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Project]:
        """
        Get all projects for a specific cursus ID.

        Args:
            cursus_id: The cursus ID to fetch projects for
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Project objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetProjectsByCursusId(cursus_id), *params)

    def get_by_id(self, project_id: int, *params: Parameter) -> Project:
        """
        Get a project by ID.

        Args:
            project_id: The project ID to fetch
            *params: Additional request parameters

        Returns:
            Project object

        Raises:
            FortyTwoNotFoundException: If project is not found
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetProjectsById(project_id), *params)

    @with_pagination
    def get_by_project_id(
        self,
        project_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Project]:
        """
        Get all sub-projects for a specific parent project ID.

        Args:
            project_id: The parent project ID to fetch sub-projects for
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Project objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetProjectsByProjectId(project_id), *params)

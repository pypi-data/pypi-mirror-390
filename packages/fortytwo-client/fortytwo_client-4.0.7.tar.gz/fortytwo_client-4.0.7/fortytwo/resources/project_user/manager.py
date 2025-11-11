from __future__ import annotations

from typing import TYPE_CHECKING

from fortytwo.request.parameter.pagination import with_pagination
from fortytwo.resources.project_user.resource import (
    GetProjectUserById,
    GetProjectUsers,
    GetProjectUsersByProject,
    GetProjectUsersByUserId,
)


if TYPE_CHECKING:
    from fortytwo.client import Client
    from fortytwo.request.parameter.parameter import Parameter
    from fortytwo.resources.project_user.project_user import ProjectUser


class ProjectUserManager:
    """
    Manager for project user-related API operations.
    """

    def __init__(self, client: Client) -> None:
        self._client = client

    def get_by_id(self, project_user_id: int, *params: Parameter) -> ProjectUser:
        """
        Get a project user by ID.

        Args:
            project_user_id: The project user ID to fetch
            *params: Additional request parameters

        Returns:
            ProjectUser object

        Raises:
            FortyTwoNotFoundException: If project user is not found
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetProjectUserById(project_user_id), *params)

    @with_pagination
    def get_all(
        self,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[ProjectUser]:
        """
        Get all project users.

        Args:
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of ProjectUser objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetProjectUsers(), *params)

    @with_pagination
    def get_by_project_id(
        self,
        project_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[ProjectUser]:
        """
        Get all project users for a specific project ID.

        Args:
            project_id: The project ID to fetch project users for
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of ProjectUser objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetProjectUsersByProject(project_id), *params)

    @with_pagination
    def get_by_user_id(
        self,
        user_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[ProjectUser]:
        """
        Get all project users for a specific user ID.

        Args:
            user_id: The user ID to fetch project users for
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of ProjectUser objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetProjectUsersByUserId(user_id), *params)

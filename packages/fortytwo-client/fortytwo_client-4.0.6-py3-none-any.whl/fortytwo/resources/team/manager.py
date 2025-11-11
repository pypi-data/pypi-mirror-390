from __future__ import annotations

from typing import TYPE_CHECKING

from fortytwo.request.parameter.pagination import with_pagination
from fortytwo.resources.team.resource import (
    GetTeams,
    GetTeamsByCursusId,
    GetTeamsByProjectId,
    GetTeamsByUserId,
    GetTeamsByUserIdAndProjectId,
)


if TYPE_CHECKING:
    from fortytwo.client import Client
    from fortytwo.request.parameter.parameter import Parameter
    from fortytwo.resources.team.team import Team


class TeamManager:
    """
    Manager for team-related API operations.
    """

    def __init__(self, client: Client) -> None:
        self._client = client

    @with_pagination
    def get_all(
        self,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Team]:
        """
        Get all teams.

        Args:
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Team objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetTeams(), *params)

    @with_pagination
    def get_by_cursus_id(
        self,
        cursus_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Team]:
        """
        Get all teams for a specific cursus ID.

        Args:
            cursus_id: The cursus ID to fetch teams for
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Team objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetTeamsByCursusId(cursus_id), *params)

    @with_pagination
    def get_by_user_id(
        self,
        user_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Team]:
        """
        Get all teams for a specific user ID.

        Args:
            user_id: The user ID to fetch teams for
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Team objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetTeamsByUserId(user_id), *params)

    @with_pagination
    def get_by_project_id(
        self,
        project_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Team]:
        """
        Get all teams for a specific project ID.

        Args:
            project_id: The project ID to fetch teams for
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Team objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetTeamsByProjectId(project_id), *params)

    @with_pagination
    def get_by_user_id_and_project_id(
        self,
        user_id: int,
        project_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Team]:
        """
        Get all teams for a specific user and project.

        Args:
            user_id: The user ID to fetch teams for
            project_id: The project ID to fetch teams for
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Team objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetTeamsByUserIdAndProjectId(user_id, project_id), *params)

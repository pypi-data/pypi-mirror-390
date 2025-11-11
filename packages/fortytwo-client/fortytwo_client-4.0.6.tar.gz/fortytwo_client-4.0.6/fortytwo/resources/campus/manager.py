from __future__ import annotations

from typing import TYPE_CHECKING

from fortytwo.request.parameter.pagination import with_pagination
from fortytwo.resources.campus.resource import GetCampusById, GetCampuses


if TYPE_CHECKING:
    from fortytwo.client import Client
    from fortytwo.request.parameter.parameter import Parameter
    from fortytwo.resources.campus.campus import Campus


class CampusManager:
    """
    Manager for campus-related API operations.
    """

    def __init__(self, client: Client) -> None:
        self._client = client

    def get_by_id(self, campus_id: int, *params: Parameter) -> Campus:
        """
        Get a campus by ID.

        Args:
            campus_id: The campus ID to fetch
            *params: Additional request parameters

        Returns:
            Campus object

        Raises:
            FortyTwoNotFoundException: If campus is not found
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetCampusById(campus_id), *params)

    @with_pagination
    def get_all(
        self,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Campus]:
        """
        Get all campuses.

        Args:
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Campus objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetCampuses(), *params)

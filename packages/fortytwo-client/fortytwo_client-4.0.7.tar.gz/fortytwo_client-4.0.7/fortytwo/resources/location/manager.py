from __future__ import annotations

from typing import TYPE_CHECKING

from fortytwo.request.parameter.pagination import with_pagination
from fortytwo.resources.location.resource import (
    GetLocationById,
    GetLocations,
    GetLocationsByCampusId,
    GetLocationsByUserId,
)


if TYPE_CHECKING:
    from fortytwo.client import Client
    from fortytwo.request.parameter.parameter import Parameter
    from fortytwo.resources.location.location import Location


class LocationManager:
    """
    Manager for location-related API operations.
    """

    def __init__(self, client: Client) -> None:
        self._client = client

    @with_pagination
    def get_all(
        self,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Location]:
        """
        Get all locations.

        Args:
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Location objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetLocations(), *params)

    def get_by_id(self, location_id: int) -> Location:
        """
        Get a location by ID.

        Args:
            location_id: The location ID to fetch

        Returns:
            Location object

        Raises:
            FortyTwoNotFoundException: If the location is not found
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetLocationById(location_id))

    @with_pagination
    def get_by_user_id(
        self,
        user_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Location]:
        """
        Get locations of a user by user ID.

        Args:
            user_id: The user ID to fetch
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Location objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetLocationsByUserId(user_id), *params)

    @with_pagination
    def get_by_campus_id(
        self,
        campus_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[Location]:
        """
        Get locations of a campus by campus ID.

        Args:
            campus_id: The campus ID to fetch
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of Location objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetLocationsByCampusId(campus_id), *params)

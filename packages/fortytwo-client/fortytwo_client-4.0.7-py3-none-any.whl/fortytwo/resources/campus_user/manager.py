from __future__ import annotations

from typing import TYPE_CHECKING

from fortytwo.request.parameter.pagination import with_pagination
from fortytwo.resources.campus_user.resource import (
    GetCampusUserById,
    GetCampusUsers,
    GetCampusUsersByUserId,
)


if TYPE_CHECKING:
    from fortytwo.client import Client
    from fortytwo.request.parameter.parameter import Parameter
    from fortytwo.resources.campus_user.campus_user import CampusUser


class CampusUserManager:
    """
    Manager for campus user-related API operations.
    """

    def __init__(self, client: Client) -> None:
        self._client = client

    def get_by_id(
        self,
        campus_user_id: int,
    ) -> CampusUser:
        """
        Get a single campus user by ID.

        Args:
            campus_user_id: The campus user ID to fetch

        Returns:
            CampusUser object

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetCampusUserById(campus_user_id))

    @with_pagination
    def get_all(
        self,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[CampusUser]:
        """
        Get all campus users.

        Args:
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of CampusUser objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetCampusUsers(), *params)

    @with_pagination
    def get_by_user_id(
        self,
        user_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[CampusUser]:
        """
        Get all campus users for a specific user ID.

        Args:
            user_id: The user ID to fetch campus users for
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of CampusUser objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetCampusUsersByUserId(user_id), *params)

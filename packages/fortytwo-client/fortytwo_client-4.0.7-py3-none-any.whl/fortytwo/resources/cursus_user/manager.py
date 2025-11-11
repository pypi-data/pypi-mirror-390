from __future__ import annotations

from typing import TYPE_CHECKING

from fortytwo.request.parameter.pagination import with_pagination
from fortytwo.resources.cursus_user.resource import (
    GetCursusUserById,
    GetCursusUsers,
    GetCursusUsersByCursusId,
    GetCursusUsersByUserId,
)


if TYPE_CHECKING:
    from fortytwo.client import Client
    from fortytwo.request.parameter.parameter import Parameter
    from fortytwo.resources.cursus_user.cursus_user import CursusUser


class CursusUserManager:
    """
    Manager for cursus user-related API operations.
    """

    def __init__(self, client: Client) -> None:
        self._client = client

    def get_by_id(
        self,
        cursus_user_id: int,
    ) -> CursusUser:
        """
        Get a single cursus user by ID.

        Args:
            cursus_user_id: The cursus user ID to fetch

        Returns:
            CursusUser object

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetCursusUserById(cursus_user_id))

    @with_pagination
    def get_all(
        self,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[CursusUser]:
        """
        Get all cursus users.

        Args:
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of CursusUser objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetCursusUsers(), *params)

    @with_pagination
    def get_by_user_id(
        self,
        user_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[CursusUser]:
        """
        Get all cursus users for a specific user ID.

        Args:
            user_id: The user ID to fetch cursus users for
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of CursusUser objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetCursusUsersByUserId(user_id), *params)

    @with_pagination
    def get_by_cursus_id(
        self,
        cursus_id: int,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[CursusUser]:
        """
        Get all cursus users for a specific cursus ID.

        Args:
            cursus_id: The cursus ID to fetch cursus users for
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of CursusUser objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetCursusUsersByCursusId(cursus_id), *params)

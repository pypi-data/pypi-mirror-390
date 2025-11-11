from __future__ import annotations

from typing import TYPE_CHECKING

from fortytwo.request.parameter.pagination import with_pagination
from fortytwo.resources.user.resource import GetUserById, GetUsers


if TYPE_CHECKING:
    from fortytwo.client import Client
    from fortytwo.request.parameter.parameter import Parameter
    from fortytwo.resources.user.user import User


class UserManager:
    """
    Manager for user-related API operations.
    """

    def __init__(self, client: Client) -> None:
        self._client = client

    def get_by_id(self, user_id: int, *params: Parameter) -> User:
        """
        Get a user by ID.

        Args:
            user_id: The user ID to fetch
            *params: Additional request parameters

        Returns:
            User object

        Raises:
            FortyTwoNotFoundException: If user is not found
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetUserById(user_id), *params)

    @with_pagination
    def get_all(
        self,
        *params: Parameter,
        page: int | None = None,
        page_size: int | None = None,
    ) -> list[User]:
        """
        Get all users.

        Args:
            *params: Additional request parameters
            page: Page number to fetch (1-indexed)
            page_size: Number of items per page (1-100)

        Returns:
            List of User objects

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetUsers(), *params)

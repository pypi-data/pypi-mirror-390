"""
Resources for fetching cursus user data from the 42 API.
"""

from typing import Any, Self

from fortytwo.resources.cursus_user.cursus_user import CursusUser
from fortytwo.resources.resource import Resource, ResourceTemplate


class GetCursusUsers(Resource[list[CursusUser]]):
    """
    Resource for fetching all cursus users.

    Returns a list of cursus users from the /cursus_users endpoint.
    Supports pagination via parameters.
    """

    method: str = "GET"
    _url: str = "/cursus_users"

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [CursusUser(cu) for cu in response_data]


class GetCursusUserById(Resource[CursusUser]):
    """
    Resource for fetching a single cursus user by ID.

    Args:
        cursus_user_id: The ID of the cursus user to fetch.
    """

    method: str = "GET"
    _url: str = "/cursus_users/%s"

    def __init__(self: Self, cursus_user_id: int) -> None:
        self.cursus_user_id = cursus_user_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.cursus_user_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return CursusUser(response_data)


class GetCursusUsersByUserId(Resource[list[CursusUser]]):
    """
    Resource for fetching all cursus users for a specific user.

    Args:
        user_id: The ID of the user to fetch cursus users for.
    """

    method: str = "GET"
    _url: str = "/users/%s/cursus_users"

    def __init__(self: Self, user_id: int) -> None:
        self.user_id = user_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.user_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [CursusUser(cu) for cu in response_data]


class GetCursusUsersByCursusId(Resource[list[CursusUser]]):
    """
    Resource for fetching all cursus users for a specific cursus.

    Args:
        cursus_id: The ID of the cursus to fetch cursus users for.
    """

    method: str = "GET"
    _url: str = "/cursus/%s/cursus_users"

    def __init__(self: Self, cursus_id: int) -> None:
        self.cursus_id = cursus_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.cursus_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [CursusUser(cu) for cu in response_data]

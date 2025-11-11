"""
Resources for fetching user data from the 42 API.
"""

from typing import Any, Self

from fortytwo.resources.resource import Resource, ResourceTemplate
from fortytwo.resources.user.user import User


class GetUsers(Resource[list[User]]):
    """
    Resource for fetching all users.

    Returns a list of users from the /users endpoint.
    Supports pagination via parameters.
    """

    method: str = "GET"
    _url: str = "/users"

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [User(user) for user in response_data]


class GetUserById(Resource[User]):
    """
    Resource for fetching a specific user by ID.

    Args:
        user_id: The ID of the user to fetch.
    """

    method: str = "GET"
    _url: str = "/users/%s"

    def __init__(self: Self, user_id: int) -> None:
        self.user_id = user_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.user_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return User(response_data)

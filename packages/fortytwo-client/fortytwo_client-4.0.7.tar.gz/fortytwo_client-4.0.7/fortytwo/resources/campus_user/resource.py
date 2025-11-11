"""
Resources for fetching campus user data from the 42 API.
"""

from typing import Any, Self

from fortytwo.resources.campus_user.campus_user import CampusUser
from fortytwo.resources.resource import Resource, ResourceTemplate


class GetCampusUsers(Resource[list[CampusUser]]):
    """
    Resource for fetching all campus users.

    Returns a list of campus users from the /campus_users endpoint.
    Supports pagination via parameters.
    """

    method: str = "GET"
    _url: str = "/campus_users"

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [CampusUser(cu) for cu in response_data]


class GetCampusUserById(Resource[CampusUser]):
    """
    Resource for fetching a single campus user by ID.

    Args:
        campus_user_id: The ID of the campus user to fetch.
    """

    method: str = "GET"
    _url: str = "/campus_users/%s"

    def __init__(self: Self, campus_user_id: int) -> None:
        self.campus_user_id = campus_user_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.campus_user_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return CampusUser(response_data)


class GetCampusUsersByUserId(Resource[list[CampusUser]]):
    """
    Resource for fetching all campus users for a specific user.

    Args:
        user_id: The ID of the user to fetch campus users for.
    """

    method: str = "GET"
    _url: str = "/users/%s/campus_users"

    def __init__(self: Self, user_id: int) -> None:
        self.user_id = user_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.user_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [CampusUser(cu) for cu in response_data]

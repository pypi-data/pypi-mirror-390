"""
Resources for fetching campus data from the 42 API.
"""

from typing import Any, Self

from fortytwo.resources.campus.campus import Campus
from fortytwo.resources.resource import Resource, ResourceTemplate


class GetCampuses(Resource[list[Campus]]):
    """
    Resource for fetching all campuses.

    Returns a list of campuses from the /campus endpoint.
    Supports pagination via parameters.
    """

    method: str = "GET"
    _url: str = "/campus"

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [Campus(campus) for campus in response_data]


class GetCampusById(Resource[Campus]):
    """
    Resource for fetching a specific campus by ID.

    Args:
        campus_id: The ID of the campus to fetch.
    """

    method: str = "GET"
    _url: str = "/campus/%s"

    def __init__(self: Self, campus_id: int) -> None:
        self.campus_id = campus_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.campus_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return Campus(response_data)

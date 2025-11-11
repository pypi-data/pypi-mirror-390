"""
Resources for fetching cursus data from the 42 API.
"""

from typing import Any, Self

from fortytwo.resources.cursus.cursus import Cursus
from fortytwo.resources.resource import Resource, ResourceTemplate


class GetCursuses(Resource[list[Cursus]]):
    """
    Resource for fetching all cursuses.

    Returns a list of cursuses from the /cursus endpoint.
    Supports pagination via parameters.
    """

    method: str = "GET"
    _url: str = "/cursus"

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [Cursus(cursus) for cursus in response_data]


class GetCursusById(Resource[Cursus]):
    """
    Resource for fetching a specific cursus by ID.

    Args:
        cursus_id: The ID of the cursus to fetch.
    """

    method: str = "GET"
    _url: str = "/cursus/%s"

    def __init__(self: Self, cursus_id: int) -> None:
        self.cursus_id = cursus_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.cursus_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return Cursus(response_data)

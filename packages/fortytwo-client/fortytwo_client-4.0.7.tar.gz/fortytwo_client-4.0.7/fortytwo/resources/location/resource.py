"""
Resources for fetching location data from the 42 API.
"""

from typing import Any, Self

from fortytwo.resources.location.location import Location
from fortytwo.resources.resource import Resource, ResourceTemplate


class GetLocations(Resource[list[Location]]):
    """
    Resource for fetching all locations.

    Returns a list of all location records from the 42 API.
    """

    method: str = "GET"
    url: str = "/locations"

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [Location(location) for location in response_data]


class GetLocationById(Resource[Location]):
    """
    Resource for fetching a specific location by ID.

    Args:
        location_id: The ID of the location to fetch.
    """

    method: str = "GET"
    _url: str = "/locations/%s"

    def __init__(self: Self, location_id: int) -> None:
        self.location_id = location_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.location_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return Location(response_data)


class GetLocationsByUserId(Resource[list[Location]]):
    """
    Resource for fetching locations for a specific user.

    Returns a list of location records showing where and when
    the user has logged in at 42 campuses.

    Args:
        user_id: The ID of the user whose locations to fetch.
    """

    method: str = "GET"
    _url: str = "/users/%s/locations"

    def __init__(self: Self, user_id: int) -> None:
        self.user_id = user_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.user_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [Location(location) for location in response_data]


class GetLocationsByCampusId(Resource[list[Location]]):
    """
    Resource for fetching locations for a specific campus.

    Returns a list of location records for all workstations
    at the given campus.

    Args:
        campus_id: The ID of the campus whose locations to fetch.
    """

    method: str = "GET"
    _url: str = "/campus/%s/locations"

    def __init__(self: Self, campus_id: int) -> None:
        self.campus_id = campus_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.campus_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [Location(location) for location in response_data]

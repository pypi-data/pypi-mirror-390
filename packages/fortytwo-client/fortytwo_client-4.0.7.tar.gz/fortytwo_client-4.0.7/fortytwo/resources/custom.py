"""
This module contains the CustomResource class.
"""

from typing import Any, Self

from fortytwo.resources.resource import Resource, ResourceTemplate


class CustomResource(Resource[Any]):
    """
    Custom resource for arbitrary 42 API endpoints.

    Allows making requests to API endpoints without defining a dedicated
    resource class. Returns raw response data without parsing.

    Args:
        method: HTTP method to use (e.g., "GET", "POST").
        url: Relative URL path for the endpoint (e.g., "/v2/users").

    Example:
        ```
        >>> resource = CustomResource("GET", "/v2/campus/1")
        >>> result = client.request(resource)

        >>> print(result)  # Raw response data
        ```
    """

    _method: str
    _url: str

    def __init__(self: Self, method: str, url: str) -> None:
        self._method = method
        self._url = url

    @property
    def method(self: Self) -> str:
        return self._method

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return response_data


__all__ = [
    "CustomResource",
]

"""
This module provides a base class for 42 API resources.
"""

from typing import Any, Self, TypeVar

from fortytwo.config import Config


ResourceTemplate = TypeVar("ResourceTemplate")


class Resource[ResourceTemplate]:
    """
    Base class for 42 API resources.

    Defines the interface for all API resource implementations.
    Subclasses must implement method, url, and parse_response properties.
    """

    config: Config

    @property
    def method(self: Self) -> str:
        """
        Get the HTTP method to use for this request.

        Returns:
            HTTP method string (e.g., "GET", "POST").

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """

        raise NotImplementedError

    @property
    def url(self: Self) -> str:
        """
        Get the full URL for this request.

        Returns:
            Complete URL string for the API endpoint.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """

        raise NotImplementedError

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        """
        Parse the API response into the appropriate type.

        Args:
            response_data: Raw response data from the API.

        Returns:
            Parsed data in the resource's template type.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """

        raise NotImplementedError

    def set_config(self: Self, config: Config) -> Self:
        """
        Set the configuration for this resource.

        Args:
            config: Configuration object to use.

        Returns:
            Self for method chaining.
        """

        self.config = config
        return self


__all__ = [
    "Resource",
]

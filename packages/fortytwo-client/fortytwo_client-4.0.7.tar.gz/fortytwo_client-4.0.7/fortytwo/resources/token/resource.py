"""
This module provides resources for getting token information.
"""

from typing import Any, Self

from fortytwo.resources.resource import Resource, ResourceTemplate
from fortytwo.resources.token.token import Token


class GetToken(Resource[Token]):
    """
    This class provides a resource for getting token information.
    """

    method: str = "GET"

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint_oauth

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return Token(response_data)

from __future__ import annotations

from typing import TYPE_CHECKING

from fortytwo.resources.token.resource import GetToken


if TYPE_CHECKING:
    from fortytwo.client import Client
    from fortytwo.request.parameter.parameter import Parameter
    from fortytwo.resources.token.token import Token


class TokenManager:
    """
    Manager for token-related API operations.
    """

    def __init__(self, client: Client) -> None:
        self._client = client

    def get(self, *params: Parameter) -> Token:
        """
        Get token information.

        Args:
            *params: Additional request parameters

        Returns:
            Token object

        Raises:
            FortyTwoRequestException: If the request fails
        """
        return self._client.request(GetToken(), *params)

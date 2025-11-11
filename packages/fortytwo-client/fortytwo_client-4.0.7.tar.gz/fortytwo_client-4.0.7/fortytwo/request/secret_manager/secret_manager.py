"""
Base secret manager interface for the 42 API client.
"""

from typing import Self

from fortytwo.request.authentication import Tokens


class SecretManager:
    """
    Abstract base class for managing 42 API authentication secrets.

    Implementations must define how to retrieve and refresh OAuth2 tokens
    for the 42 API.
    """

    def get_tokens(self: Self, endpoint_oauth: str) -> Tokens:
        """
        Retrieve the current 42 API tokens.

        Returns:
            Tokens object containing authentication tokens.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def refresh_tokens(self: Self, endpoint_oauth: str) -> Tokens:
        """
        Refresh and retrieve updated 42 API tokens.

        Returns:
            Tokens object with fresh authentication tokens.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

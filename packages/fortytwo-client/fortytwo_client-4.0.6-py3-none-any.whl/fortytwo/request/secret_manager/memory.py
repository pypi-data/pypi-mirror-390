"""
In-memory secret manager implementation for the 42 API client.
"""

from typing import Self

from fortytwo.request.authentication import Authentication, Tokens
from fortytwo.request.secret_manager.secret_manager import SecretManager


class MemorySecretManager(SecretManager):
    """
    In-memory secret manager implementation.

    Stores credentials in memory and fetches tokens as needed.
    Suitable for simple use cases where credential rotation is not required.
    """

    def __init__(self: Self, client_id: str, client_secret: str) -> None:
        """
        Initialize the memory secret manager with static credentials.

        Args:
            client_id: The 42 API client ID.
            client_secret: The 42 API client secret.
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: Tokens | None = None

    def get_tokens(self: Self, endpoint_oauth: str) -> Tokens:
        """
        Retrieve the 42 API tokens, fetching new ones if necessary.

        Returns:
            Tokens object containing authentication tokens.
        """

        if self._token is None or self._token.is_expired():
            self.refresh_tokens(endpoint_oauth)

        return self._token

    def refresh_tokens(self: Self, endpoint_oauth: str) -> Tokens:
        """
        Fetch fresh tokens from the 42 API.

        Returns:
            Tokens object with new authentication tokens.

        Raises:
            FortyTwoAuthException: If token refresh fails.
        """

        self._token = Authentication.fetch_tokens(
            client_id=self._client_id,
            client_secret=self._client_secret,
            endpoint_oauth=endpoint_oauth,
        )

        return self._token

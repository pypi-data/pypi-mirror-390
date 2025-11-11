"""
A secret manager that retrieves credentials from HashiCorp Vault.
"""

from typing import Any, Self

from fortytwo.exceptions import FortyTwoAuthException
from fortytwo.request.authentication import Authentication, Tokens
from fortytwo.request.secret_manager.secret_manager import SecretManager


class VaultSecretManager(SecretManager):
    """
    A secret manager that retrieves credentials from HashiCorp Vault.
    """

    def __init__(self: Self, vault_client: Any, path: str, mount_point: str) -> None:
        """
        Initialize the Vault secret manager.
        """
        self._vault = vault_client
        self._path = path
        self._mount_point = mount_point
        self._token: Tokens | None = None

    def get_tokens(self: Self, endpoint_oauth: str) -> Tokens:
        """
        Retrieve the 42 API tokens.

        Returns:
            Tokens: The access and refresh tokens.
        """

        if self._token is None or self._token.is_expired():
            self.refresh_tokens(endpoint_oauth)

        return self._token

    def refresh_tokens(self: Self, endpoint_oauth: str) -> Tokens:
        """
        Refresh tokens (returns new tokens using the same credentials).

        Returns:
            Tokens: The refreshed access and refresh tokens.
        """

        try:
            secrets = self._vault.secrets.kv.read_secret_version(
                path=self._path,
                mount_point=self._mount_point,
            )

            data = secrets["data"]["data"]
            client_id = data["client_id"]
            client_secret = data["client_secret"]

            self._token = Authentication.fetch_tokens(
                client_id=client_id,
                client_secret=client_secret,
                endpoint_oauth=endpoint_oauth,
            )

            return self._token
        except Exception as e:
            raise FortyTwoAuthException("Failed to refresh tokens from Vault") from e

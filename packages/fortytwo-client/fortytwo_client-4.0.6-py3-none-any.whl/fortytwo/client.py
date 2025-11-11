from __future__ import annotations

from typing import TYPE_CHECKING, Self

from fortytwo.config import Config
from fortytwo.request.handler import RequestHandler
from fortytwo.request.secret_manager import (
    MemorySecretManager,
    VaultSecretManager,
)
from fortytwo.resources.campus import CampusManager
from fortytwo.resources.campus_user import CampusUserManager
from fortytwo.resources.cursus import CursusManager
from fortytwo.resources.cursus_user import CursusUserManager
from fortytwo.resources.location import LocationManager
from fortytwo.resources.project import ProjectManager
from fortytwo.resources.project_user import ProjectUserManager
from fortytwo.resources.team import TeamManager
from fortytwo.resources.token import TokenManager
from fortytwo.resources.user import UserManager


if TYPE_CHECKING:
    from requests import Response

    from fortytwo.request.parameter.parameter import Parameter
    from fortytwo.resources.resource import Resource, ResourceTemplate


class Client:
    """
    This class provides a client for the 42 School API.
    """

    Config = Config

    class SecretManager:
        Memory = MemorySecretManager
        Vault = VaultSecretManager

    def __init__(
        self: Self,
        client_id: str | None = None,
        client_secret: str | None = None,
        config: Config | None = None,
    ) -> None:
        """
        Initialize the Client with authentication and configuration.

        Args:
            client_id: The client ID for authentication. Can be None if using a
                custom SecretManager in config.
            client_secret: The client secret for authentication. Can be None if using a
                custom SecretManager in config.
            config: Optional configuration object. If not provided, a default configuration is used.
        """
        self._config = config or Config()

        if self._config.secret_manager is None:
            self._config.secret_manager = MemorySecretManager(client_id, client_secret)

        self._request_handler = RequestHandler(
            self._config,
        )

        self.secret_manager = self._config.secret_manager

        # fmt: off
        self.campuses       = CampusManager(self)
        self.campus_users   = CampusUserManager(self)
        self.cursuses       = CursusManager(self)
        self.cursus_users   = CursusUserManager(self)
        self.users          = UserManager(self)
        self.locations      = LocationManager(self)
        self.projects       = ProjectManager(self)
        self.project_users  = ProjectUserManager(self)
        self.teams          = TeamManager(self)
        self.tokens         = TokenManager(self)
        # fmt: on

    def request(
        self: Self,
        resource: Resource[ResourceTemplate],
        *params: Parameter,
    ) -> ResourceTemplate:
        """
        Send a request to the API and return the response.

        Args:
            resource: The resource to fetch.
            *params: The parameters for the request.

        Returns:
            The response from the API.

        Raises:
            FortyTwoNotFoundException: If the resource is not found (404).
            FortyTwoAuthException: If authentication fails.
            FortyTwoRequestException: If the request fails for other reasons.
        """

        return self._request_handler.execute(resource, *params)

    @property
    def response(self: Self) -> Response | None:
        """
        Get the last response received by the client.

        Returns:
            The last response object.
        """
        return self._request_handler.response

    @property
    def total(self: Self) -> int | None:
        """
        Get the total number of items.

        Returns:
            The total number of items from the 'x-total' header.
        """
        if self.response is None:
            return None

        total = self.response.headers.get("x-total", None)
        return int(total) if total is not None else None

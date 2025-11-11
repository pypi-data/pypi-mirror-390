from __future__ import annotations

import json
from typing import TYPE_CHECKING, Self, TypeVar

import requests

from fortytwo.logger import logger


if TYPE_CHECKING:
    from fortytwo.request.authentication import Tokens
    from fortytwo.request.parameter.parameter import Parameter
    from fortytwo.resources.resource import Resource

RequestTemplate = TypeVar("RequestTemplate")


class Request[RequestTemplate]:
    """
    Represents an HTTP request to the 42 API.
    """

    def __init__(self: Self, resource: Resource, *params: Parameter) -> None:
        self._resource: Resource[RequestTemplate] = resource
        self._params: list[Parameter] = list(params)

    def add_params(self: Self, *params: Parameter) -> None:
        """
        This function adds parameters to the request.

        Args:
            *params (Parameter): The parameters to add.
        """

        self._params.extend(params)

    def request(
        self: Self,
        tokens: Tokens,
        request_timeout: int | None = None,
    ) -> requests.Response:
        """
        This function sends a request to the API and returns the response.

        Args:
            tokens (Tokens): The access and refresh tokens.
            request_timeout: Request timeout in seconds.

        Returns:
            The response from the request.

        Raises:
            HTTPError: If the HTTP request fails.
        """

        headers = {"Authorization": f"Bearer {tokens.access_token}"}
        params = [param.to_query_param() for param in self._params]
        logger.info(
            "Making request to %s?%s",
            self._resource.url,
            "&".join(f"{p[0]}={p[1]}" for p in params),
        )

        response = requests.request(
            method=self._resource.method,
            url=self._resource.url,
            headers=headers,
            params=[param.to_query_param() for param in self._params],
            timeout=request_timeout,
        )

        logger.info("Received response (%d)", response.status_code)
        logger.debug("Response headers: %s", json.dumps(dict(response.headers), indent=2))

        try:
            response_json = response.json()
            logger.debug("Response content: %s", json.dumps(response_json, indent=2))
        except (json.JSONDecodeError, requests.exceptions.JSONDecodeError):
            logger.debug("Response content (non-JSON): %s", response.text[:1000])

        response.raise_for_status()
        return response

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from requests.exceptions import HTTPError, RequestException

from fortytwo.exceptions import (
    FortyTwoNetworkException,
    FortyTwoNotFoundException,
    FortyTwoRateLimitException,
    FortyTwoRequestException,
    FortyTwoServerException,
    FortyTwoUnauthorizedException,
)
from fortytwo.logger import logger
from fortytwo.request.request import Request
from fortytwo.resources.resource import ResourceTemplate


if TYPE_CHECKING:
    from requests import Response

    from fortytwo.config import Config
    from fortytwo.request.parameter.parameter import Parameter
    from fortytwo.resources.resource import Resource


class RequestHandler:
    """
    Handles request execution, authentication, and error handling for the 42 API.
    """

    def __init__(
        self,
        config: Config,
    ) -> None:
        """
        Initialize the request handler.

        Args:
            config: Configuration object containing API settings and secret manager.
        """
        self.response: Response | None = None

        self._config = config
        self._secret_manager = config.secret_manager

        self._second_rate_limit_retry_count = 0
        self._rate_limit_remaining = self._config.requests_per_hour_margin + 1
        self._current_hour_start = self._get_current_hour_start()
        self._request_time = 0.0

    def execute(
        self,
        resource: Resource[ResourceTemplate],
        *params: Parameter,
    ) -> ResourceTemplate:
        """
        Execute a request to the 42 API with error handling.

        Args:
            resource: The API resource to fetch.
            *params: Query parameters for the request.

        Returns:
            Parsed response data in the resource's type.

        Raises:
            FortyTwoRateLimitException: When rate limit is exceeded.
            FortyTwoNotFoundException: When resource is not found (404).
            FortyTwoUnauthorizedException: When authentication fails (401).
            FortyTwoServerException: When server errors occur (5xx).
            FortyTwoNetworkException: When network errors occur.
            FortyTwoRequestException: For other request-related errors.
        """
        self._resource = resource
        self._request = Request[ResourceTemplate](resource.set_config(self._config), *params)

        self._second_rate_limit_retry_count = 0

        return self._make_request()

    def _make_request(self) -> ResourceTemplate:
        """
        Execute the request with error handling.

        Raises:
            FortyTwoRateLimitException: When rate limit is exceeded.
            FortyTwoNetworkException: When network errors occur.
            FortyTwoParsingException: When response parsing fails.
            FortyTwoRequestException: For other request-related errors.
        """

        current_hour_start = self._get_current_hour_start()
        if current_hour_start > self._current_hour_start:
            self._rate_limit_remaining = self._config.requests_per_hour_margin + 1
            self._current_hour_start = current_hour_start

        if self._rate_limit_remaining <= self._config.requests_per_hour_margin:
            return self._handle_rate_limit()

        time_elapsed = time.perf_counter() - self._request_time
        sleep_duration = (1 / self._config.requests_per_second) - time_elapsed

        if sleep_duration > 0:
            logger.debug("Sleeping for %.3f seconds to respect rate limit", sleep_duration)
            time.sleep(sleep_duration)

        try:
            response = self._request.request(
                self._secret_manager.get_tokens(self._config.request_endpoint_oauth),
                self._config.request_timeout,
            )

            rate_limit_remaining = response.headers.get(
                "x-hourly-ratelimit-remaining",
                self._config.requests_per_hour_margin + 1,
            )
            try:
                self._rate_limit_remaining = int(rate_limit_remaining)
            except ValueError:
                logger.warning("Invalid rate limit remaining value: %s", rate_limit_remaining)
                self._rate_limit_remaining = self._config.requests_per_hour_margin + 1
            logger.info("Rate limit remaining: %d requests", self._rate_limit_remaining)

            self.response = response
            self._request_time = time.perf_counter()

            response_json = response.json()
            return self._resource.parse_response(response_json)

        except HTTPError as e:
            return self._handle_http_exception(e.response)

        except RequestException as e:
            logger.error("Network error occurred: %s", e)
            raise FortyTwoNetworkException(
                f"Network error occurred while communicating with the API: {e}",
            ) from e

        except Exception as e:
            logger.error("Unexpected error occurred: %s", e)
            raise FortyTwoRequestException(
                f"Unexpected error occurred: {e}",
            ) from e

    def _handle_http_exception(self, response: Response) -> ResourceTemplate:
        """
        Handle HTTP exceptions based on status codes.

        Raises:
            FortyTwoRateLimitException: When rate limit (429) is encountered.
            FortyTwoUnauthorizedException: When unauthorized (401) after retry.
            FortyTwoNotFoundException: When resource not found (404).
            FortyTwoServerException: For server errors (5xx).
            FortyTwoRequestException: For other HTTP errors.
        """
        if response.status_code == 429:
            return self._handle_rate_limit()

        if response.status_code == 401:
            return self._handle_unauthorized(response)

        if response.status_code == 404:
            logger.error("Resource not found (404): %s", response.reason)
            raise FortyTwoNotFoundException(
                f"Requested resource not found: {response.reason}",
                error_code=404,
            )

        if 500 <= response.status_code < 600:
            logger.error("Server error (%s): %s", response.status_code, response.reason)
            raise FortyTwoServerException(
                f"Server error ({response.status_code}): {response.reason}",
                error_code=response.status_code,
            )

        logger.error(
            "Request failed (%s): %s",
            response.status_code,
            response.reason,
        )
        raise FortyTwoRequestException(
            f"Request failed ({response.status_code}): {response.reason}",
            error_code=response.status_code,
        )

    def _handle_unauthorized(self, response: Response) -> ResourceTemplate:
        """
        Handle 401 unauthorized responses by refreshing the token.

        Raises:
            FortyTwoUnauthorizedException: If token refresh fails or unauthorized persists.
        """
        logger.info("Access token expired, fetching a new one")

        try:
            self._secret_manager.refresh_tokens(self._config.request_endpoint_oauth)
            return self._make_request()
        except Exception as e:
            logger.error("Failed to refresh tokens: %s", e)
            raise FortyTwoUnauthorizedException(
                "Failed to authenticate: Token refresh failed",
                error_code=401,
            ) from e

    def _handle_rate_limit(self) -> ResourceTemplate:
        """
        Handle 429 rate limit responses.
        """
        wait_time = self._calculate_hour_reset_wait_time()

        if self._rate_limit_remaining <= self._config.requests_per_hour_margin:
            logger.error("Hourly rate limit exceeded. Reset in %.0fs", wait_time)
            raise FortyTwoRateLimitException(
                "Hourly rate limit exceeded.",
                wait_time=wait_time,
            )

        if self._second_rate_limit_retry_count >= self._config.requests_per_second_retries:
            logger.error(
                "Per-second rate limit: Max retries (%d) exceeded",
                self._config.requests_per_second_retries,
            )
            raise FortyTwoRateLimitException(
                f"Rate limit exceeded after {self._second_rate_limit_retry_count} retries.",
                wait_time=wait_time,
            )

        retry_delay = self._config.requests_per_second_retry_delay * (
            2**self._second_rate_limit_retry_count
        )
        self._second_rate_limit_retry_count += 1

        logger.info(
            "Per-second rate limit hit (retry %d/%d), waiting %.1fs...",
            self._second_rate_limit_retry_count,
            self._config.requests_per_second_retries,
            retry_delay,
        )
        time.sleep(retry_delay)

        return self._make_request()

    def _get_current_hour_start(self) -> float:
        """
        Get the start time of the current hour.
        """
        current_time = time.time()
        return current_time - (current_time % 3600)

    def _calculate_hour_reset_wait_time(self) -> float:
        """
        Calculate seconds until the hourly rate limit resets.
        """
        current_time = time.time()
        reset_time = self._current_hour_start + 3600
        return max(0.0, reset_time - current_time) + 1.0  # Add 1 second buffer

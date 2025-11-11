from dataclasses import dataclass

from fortytwo.default import (
    FORTYTWO_REQUEST_ENDPOINT,
    FORTYTWO_REQUEST_ENDPOINT_OAUTH,
    FORTYTWO_REQUEST_PER_HOUR,
    FORTYTWO_REQUEST_PER_HOUR_MARGIN,
    FORTYTWO_REQUEST_PER_SECOND,
    FORTYTWO_REQUEST_PER_SECOND_RETRIES,
    FORTYTWO_REQUEST_PER_SECOND_RETRY_DELAY,
    FORTYTWO_REQUEST_TIMEOUT,
)
from fortytwo.request.secret_manager import SecretManager


@dataclass
class Config:
    """
    Configuration for the 42 API Client.

    Attributes:
        request_timeout: Request timeout in seconds (default: 120).
        request_endpoint: Base API endpoint URL.
        request_endpoint_oauth: OAuth token endpoint URL.
        requests_per_second: Maximum number of requests per second (default: 2).
        requests_per_second_retries: Number of retries when rate limited per second (default: 5).
        requests_per_second_retry_delay: Delay between retries when rate limited per second in seconds (default: 1).
        requests_per_hour: Maximum number of requests per hour (default: 1200).
        requests_per_hour_margin: Margin to avoid hitting the hourly rate limit (default: 0).
        secret_manager: Secret manager for credentials (default: None, set by Client).
    """

    # fmt: off
    request_timeout: int                    = FORTYTWO_REQUEST_TIMEOUT  # seconds
    request_endpoint: str                   = FORTYTWO_REQUEST_ENDPOINT
    request_endpoint_oauth: str             = FORTYTWO_REQUEST_ENDPOINT_OAUTH

    requests_per_second: int                = FORTYTWO_REQUEST_PER_SECOND
    requests_per_second_retries: int        = FORTYTWO_REQUEST_PER_SECOND_RETRIES
    requests_per_second_retry_delay: int    = FORTYTWO_REQUEST_PER_SECOND_RETRY_DELAY # seconds

    requests_per_hour: int                  = FORTYTWO_REQUEST_PER_HOUR
    requests_per_hour_margin: int           = FORTYTWO_REQUEST_PER_HOUR_MARGIN

    secret_manager: SecretManager | None    = None
    # fmt: on

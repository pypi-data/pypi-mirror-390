from typing import Self


class FortyTwoClientException(Exception):
    """
    Base exception for all 42 API client errors.

    Args:
        message: Error message description.
        error_code: Optional HTTP status code or error identifier.
    """

    def __init__(
        self: Self,
        message: str = "An error occurred in the Client.",
        error_code: int | None = None,
    ) -> None:
        self.error_code = error_code
        super().__init__(message)


class FortyTwoAuthException(FortyTwoClientException):
    """
    Exception raised when authentication with the 42 API fails.
    """

    def __init__(
        self: Self,
        message: str = "An error occurred when authenticating.",
        error_code: int | None = None,
    ) -> None:
        super().__init__(message, error_code)


class FortyTwoRequestException(FortyTwoClientException):
    """
    Exception raised when an API request fails.
    """

    def __init__(
        self: Self,
        message: str = "An error occurred in the Client request.",
        error_code: int | None = None,
    ) -> None:
        super().__init__(message, error_code)


class FortyTwoRateLimitException(FortyTwoClientException):
    """
    Exception raised when rate limit is exceeded.
    """

    def __init__(
        self: Self,
        message: str = "Rate limit exceeded.",
        wait_time: float = 0.0,
        error_code: int = 429,
    ) -> None:
        self.wait_time = wait_time
        super().__init__(message, error_code)


class FortyTwoNetworkException(FortyTwoClientException):
    """
    Exception raised for network-related errors.
    """

    def __init__(
        self: Self,
        message: str = "Network error occurred while communicating with the API.",
        error_code: int | None = None,
    ) -> None:
        super().__init__(message, error_code)


class FortyTwoParsingException(FortyTwoClientException):
    """
    Exception raised when response parsing fails.
    """

    def __init__(
        self: Self,
        message: str = "Failed to parse API response.",
        error_code: int | None = None,
    ) -> None:
        super().__init__(message, error_code)


class FortyTwoNotFoundException(FortyTwoClientException):
    """
    Exception raised when a requested resource is not found.
    """

    def __init__(
        self: Self,
        message: str = "Requested resource not found.",
        error_code: int = 404,
    ) -> None:
        super().__init__(message, error_code)


class FortyTwoUnauthorizedException(FortyTwoAuthException):
    """
    Exception raised when authentication fails or token is invalid.
    """

    def __init__(
        self: Self,
        message: str = "Unauthorized: Authentication failed or token is invalid.",
        error_code: int = 401,
    ) -> None:
        super().__init__(message, error_code)


class FortyTwoServerException(FortyTwoClientException):
    """
    Exception raised for server-side errors (5xx status codes).
    """

    def __init__(
        self: Self,
        message: str = "Server error occurred.",
        error_code: int | None = None,
    ) -> None:
        super().__init__(message, error_code)

"""
Logging configuration for the fortytwo client library.

This module provides a centralized logger that can be configured by library users.
By default, the library uses a NullHandler to avoid interfering with application
logging configuration, following best practices for library logging.

Example:
    import logging
    from fortytwo import logger

    # Configure logging in your application
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(handler)
"""

import logging


logger = logging.getLogger("fortytwo")
logger.addHandler(logging.NullHandler())
logger.propagate = True


def configure_logger(
    level: int = logging.INFO,
    format_string: str | None = None,
    handler: logging.Handler | None = None,
) -> None:
    """
    Configure the fortytwo logger with common settings.

    This is a convenience function for users who want quick logging setup.
    For advanced configuration, users should configure the logger directly.

    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
        format_string: Custom format string for log messages. If None, uses default.
        handler: Custom handler to use. If None, adds a StreamHandler to stdout.

    Example:
    ```
        from fortytwo.logger import configure_logger
        import logging

        # Simple configuration
        configure_logger(level=logging.DEBUG)

        # Custom format
        configure_logger(
            level=logging.INFO,
            format_string='%(asctime)s [%(levelname)s] %(message)s'
        )
    ```
    """
    # Remove existing handlers except NullHandler
    logger.handlers = [h for h in logger.handlers if isinstance(h, logging.NullHandler)]

    logger.setLevel(level)

    if handler is None:
        handler = logging.StreamHandler()

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False


def disable_logging() -> None:
    """
    Disable all logging from the fortytwo library.

    This sets the logger level to CRITICAL+1, effectively disabling all log output.
    Useful for production environments or testing where log output is not desired.

    Example:
    ```
        from fortytwo.logger import disable_logging
        disable_logging()
    ```
    """
    logger.setLevel(logging.CRITICAL + 1)


def enable_debug_logging(level: int = logging.DEBUG) -> None:
    """
    Enable debug logging with a default configuration.

    This is a convenience function that configures the logger with a detailed
    format string including function names and line numbers. Useful for
    development and troubleshooting.

    Args:
        level: Logging level (default: logging.DEBUG). Can be set to any
            standard logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Example:
    ```
        from fortytwo.logger import enable_debug_logging
        import logging

        # Enable with DEBUG level (default)
        enable_debug_logging()

        # Enable with INFO level for less verbosity
        enable_debug_logging(level=logging.INFO)
    ```
    """
    configure_logger(
        level=level,
        format_string="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    )

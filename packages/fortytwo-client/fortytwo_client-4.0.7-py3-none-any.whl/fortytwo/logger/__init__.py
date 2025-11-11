"""
Logging utilities for the FortyTwo API client.

This module provides logger configuration and convenience functions.
"""

from fortytwo.logger.logger import (
    configure_logger,
    disable_logging,
    enable_debug_logging,
    logger,
)


__all__ = [
    "configure_logger",
    "disable_logging",
    "enable_debug_logging",
    "logger",
]

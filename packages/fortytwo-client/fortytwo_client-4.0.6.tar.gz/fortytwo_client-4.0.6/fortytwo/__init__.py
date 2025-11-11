"""
FortyTwo API Client - Main package exports.

This module exports the primary user-facing components:
- Client: Main API client
- Config: Configuration class

Submodules:
- logger: Logging utilities
- exceptions: Exception classes
- resources: API resources
- parameter: Query parameters
- secret_manager: Secret management
"""

from fortytwo import exceptions, json, logger, resources
from fortytwo.client import Client
from fortytwo.config import Config
from fortytwo.request import parameter, secret_manager


__all__ = [
    "Client",
    "Config",
    "exceptions",
    "json",
    "logger",
    "parameter",
    "resources",
    "secret_manager",
]

"""
Token resource for the FortyTwo API.

This module provides the Token model and TokenManager for interacting
with token data.
"""

from fortytwo.resources.token.manager import TokenManager
from fortytwo.resources.token.token import Token


__all__ = [
    "Token",
    "TokenManager",
]

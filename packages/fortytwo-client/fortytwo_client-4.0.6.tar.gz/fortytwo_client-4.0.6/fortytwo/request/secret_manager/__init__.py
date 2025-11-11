"""
Secret manager implementations for the 42 API client.
"""

from fortytwo.request.secret_manager.memory import MemorySecretManager
from fortytwo.request.secret_manager.secret_manager import SecretManager
from fortytwo.request.secret_manager.vault import VaultSecretManager


__all__ = [
    "MemorySecretManager",
    "SecretManager",
    "VaultSecretManager",
]

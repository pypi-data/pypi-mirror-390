"""
This module provides a base class for 42 API resource models.
"""

import json
from collections.abc import Iterator
from typing import Any, Self

from fortytwo.json import default_serializer


class Model:
    """
    Base class for all 42 API resource models.

    Provides dictionary-style access to model attributes, allowing
    both `model.attribute` and `model['attribute']` syntax.
    """

    def __getitem__(self: Self, key: str) -> Any:
        """
        Get an attribute value using dictionary-style access.

        Args:
            key: The attribute name to access.

        Returns:
            The value of the requested attribute.

        Raises:
            KeyError: If the attribute does not exist.

        Examples:
            ```
            >>> user = User(data)
            >>> user['login']  # Same as user.login
            'jdoe'
            ```
        """
        try:
            return getattr(self, key)
        except AttributeError as e:
            raise KeyError(f"{key} not found in {self.__class__.__name__}") from e

    def __contains__(self: Self, key: str) -> bool:
        """
        Check if an attribute exists in the model.

        Args:
            key: The attribute name to check.

        Returns:
            True if the attribute exists, False otherwise.

        Examples:
            ```
            >>> user = User(data)
            >>> 'login' in user
            True
            >>> 'nonexistent' in user
            False
            ```
        """
        return hasattr(self, key)

    def __eq__(self: Self, other: object) -> bool:
        """
        Compare two models for equality.

        Args:
            other: Another object to compare with.

        Returns:
            True if both models are of the same type and have equal attributes.

        Examples:
            ```
            >>> user1 = User(data)
            >>> user2 = User(data)
            >>> user1 == user2
            True
            ```
        """
        if not isinstance(other, self.__class__):
            return False
        return self.to_dict() == other.to_dict()

    def get(self: Self, key: str, default: Any = None) -> Any:
        """
        Get an attribute value with a default fallback.

        Args:
            key: The attribute name to access.
            default: Default value to return if attribute doesn't exist.

        Returns:
            The attribute value or default if not found.

        Examples:
            ```
            >>> user = User(data)
            >>> user.get('login', 'unknown')
            'jdoe'
            >>> user.get('nonexistent', 'default')
            'default'
            ```
        """
        return getattr(self, key, default)

    def keys(self: Self) -> Iterator[str]:
        """
        Get all attribute names (excluding private/magic attributes).

        Returns:
            Iterator of attribute names.

        Examples:
            ```
            >>> user = User(data)
            >>> list(user.keys())
            ['id', 'login', 'kind', 'alumni', 'active', ...]
            ```
        """
        return (key for key in self.__dict__ if not key.startswith("_"))

    def values(self: Self) -> Iterator[Any]:
        """
        Get all attribute values (excluding private/magic attributes).

        Returns:
            Iterator of attribute values.

        Examples:
            ```
            >>> user = User(data)
            >>> list(user.values())
            [123, 'jdoe', 'student', False, True, ...]
            ```
        """
        return (value for key, value in self.__dict__.items() if not key.startswith("_"))

    def items(self: Self) -> Iterator[tuple[str, Any]]:
        """
        Get attribute name-value pairs (excluding private/magic attributes).

        Returns:
            Iterator of (name, value) tuples.

        Examples:
            ```
            >>> user = User(data)
            >>> list(user.items())
            [('id', 123), ('login', 'jdoe'), ('kind', 'student'), ...]
            ```
        """
        return ((key, value) for key, value in self.__dict__.items() if not key.startswith("_"))

    def to_dict(self: Self) -> dict[str, Any]:
        """
        Convert the model to a plain dictionary.

        Returns:
            Dictionary containing all non-private attributes.

        Examples:
            ```
            >>> user = User(data)
            >>> user.to_dict()
            {'id': 123, 'login': 'jdoe', 'kind': 'student', ...}
            ```
        """
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}

    def to_json(self: Self, *args: Any, **kwargs: Any) -> str:
        """
        Serialize the model to a JSON string.

        Args:
            *args: Positional arguments to pass to json.dumps().
            **kwargs: Keyword arguments to pass to json.dumps().

        Returns:
            JSON string representation of the model.

        Examples:
            ```
            >>> user = User(data)
            >>> user.to_json()
            '{"id": 123, "login": "jdoe", "kind": "student", ...}'
            ```
        """
        return json.dumps(self, *args, default=default_serializer, **kwargs)


__all__ = [
    "Model",
]

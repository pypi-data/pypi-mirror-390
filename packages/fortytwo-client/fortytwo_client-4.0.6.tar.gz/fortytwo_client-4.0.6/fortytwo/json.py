from collections.abc import Callable
from typing import Any


SERIALIZERS = {}


def register_serializer(cls: type, func: Callable[[Any], dict[str, Any]]) -> None:
    SERIALIZERS[cls] = func


def default_serializer(obj: Any) -> Any:
    for cls, serializer_func in SERIALIZERS.items():
        if isinstance(obj, cls):
            return serializer_func(obj)

    raise TypeError(f"Type {obj.__class__.__name__} not serializable")


__all__ = [
    "default_serializer",
    "register_serializer",
]

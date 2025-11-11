"""
Pagination functions and decorators for the fortytwo client library.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar


PaginatedFunctionTemplate = TypeVar("PaginatedFunctionTemplate", bound=Callable[..., Any])


def with_pagination[PaginatedFunctionTemplate: Callable[..., Any]](
    func: PaginatedFunctionTemplate,
) -> PaginatedFunctionTemplate:
    """
    Decorator that automatically handles pagination parameters.

    This decorator extracts 'page' and 'page_size' keyword arguments from the
    function call and converts them to PageNumber and PageSize parameters,
    which are then passed to the underlying request method.

    Args:
        func: The function to decorate

    Returns:
        The decorated function

    Example:
        @with_pagination
        def get_all(self, *params):
            return self._client.request(GetUsers(), *params)

        # Can now be called with pagination
        get_all(page=1, page_size=50)
    """
    from fortytwo.request.parameter.parameter import PageNumber, PageSize

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Extract pagination parameters
        page = kwargs.pop("page", None)
        page_size = kwargs.pop("page_size", None)

        pagination_params = []
        if page is not None:
            pagination_params.append(PageNumber(page))
        if page_size is not None:
            pagination_params.append(PageSize(page_size))

        # Call original function with pagination params added to positional args
        return func(*args, *pagination_params, **kwargs)

    return wrapper

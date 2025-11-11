from datetime import datetime

from fortytwo.request.parameter.parameter import Filter


class CursusFilter:
    """
    Filter class specifically for cursus resources with all supported 42 API filters.
    """

    @staticmethod
    def by_id(cursus_id: str | int) -> Filter:
        """
        Filter cursuses by ID.

        Args:
            cursus_id (Union[str, int]): The cursus ID to filter by.
        """
        return Filter("id", [cursus_id])

    @staticmethod
    def by_name(name: str) -> Filter:
        """
        Filter cursuses by name.

        Args:
            name (str): The cursus name to filter by.
        """
        return Filter("name", [name])

    @staticmethod
    def by_created_at(created_at: str | datetime) -> Filter:
        """
        Filter cursuses by created date.

        Args:
            created_at (Union[str, datetime]): The creation date to filter by (ISO format string or datetime object).
        """
        return Filter("created_at", [created_at])

    @staticmethod
    def by_updated_at(updated_at: str | datetime) -> Filter:
        """
        Filter cursuses by updated date.

        Args:
            updated_at (Union[str, datetime]): The update date to filter by (ISO format string or datetime object).
        """
        return Filter("updated_at", [updated_at])

    @staticmethod
    def by_slug(slug: str) -> Filter:
        """
        Filter cursuses by slug.

        Args:
            slug (str): The slug to filter by.
        """
        return Filter("slug", [slug])

    @staticmethod
    def by_kind(kind: str) -> Filter:
        """
        Filter cursuses by kind.

        Args:
            kind (str): The kind to filter by.
        """
        return Filter("kind", [kind])

    @staticmethod
    def by_restricted(restricted: bool) -> Filter:
        """
        Filter cursuses by restricted status.

        Args:
            restricted (bool): The restricted status to filter by.
        """
        return Filter("restricted", [restricted])

    @staticmethod
    def by_is_subscriptable(is_subscriptable: bool) -> Filter:
        """
        Filter cursuses by subscriptable status.

        Args:
            is_subscriptable (bool): The subscriptable status to filter by.
        """
        return Filter("is_subscriptable", [is_subscriptable])

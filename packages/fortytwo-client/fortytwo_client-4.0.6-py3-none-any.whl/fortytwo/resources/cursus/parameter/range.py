from datetime import datetime

from fortytwo.request.parameter.parameter import Range


class CursusRange:
    """
    Range class specifically for cursus resources with all supported 42 API range options.
    """

    @staticmethod
    def id_range(min_id: str | int | None = None, max_id: str | int | None = None) -> Range:
        """
        Filter cursuses by ID range.

        Args:
            min_id (Union[str, int], optional): Minimum ID value.
            max_id (Union[str, int], optional): Maximum ID value.
        """
        return Range("id", [min_id, max_id])

    @staticmethod
    def name_range(min_name: str | None = None, max_name: str | None = None) -> Range:
        """
        Filter cursuses by name range (alphabetical).

        Args:
            min_name (str, optional): Minimum name value.
            max_name (str, optional): Maximum name value.
        """
        return Range("name", [min_name, max_name])

    @staticmethod
    def created_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter cursuses by created date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("created_at", [start_date, end_date])

    @staticmethod
    def updated_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter cursuses by updated date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("updated_at", [start_date, end_date])

    @staticmethod
    def slug_range(min_slug: str | None = None, max_slug: str | None = None) -> Range:
        """
        Filter cursuses by slug range (alphabetical).

        Args:
            min_slug (str, optional): Minimum slug value.
            max_slug (str, optional): Maximum slug value.
        """
        return Range("slug", [min_slug, max_slug])

    @staticmethod
    def kind_range(min_kind: str | None = None, max_kind: str | None = None) -> Range:
        """
        Filter cursuses by kind range (alphabetical).

        Args:
            min_kind (str, optional): Minimum kind value.
            max_kind (str, optional): Maximum kind value.
        """
        return Range("kind", [min_kind, max_kind])

    @staticmethod
    def restricted_range(
        min_restricted: bool | None = None, max_restricted: bool | None = None
    ) -> Range:
        """
        Filter cursuses by restricted status range.

        Args:
            min_restricted (bool, optional): Minimum restricted value.
            max_restricted (bool, optional): Maximum restricted value.
        """
        return Range("restricted", [min_restricted, max_restricted])

    @staticmethod
    def is_subscriptable_range(
        min_is_subscriptable: bool | None = None, max_is_subscriptable: bool | None = None
    ) -> Range:
        """
        Filter cursuses by subscriptable status range.

        Args:
            min_is_subscriptable (bool, optional): Minimum subscriptable value.
            max_is_subscriptable (bool, optional): Maximum subscriptable value.
        """
        return Range("is_subscriptable", [min_is_subscriptable, max_is_subscriptable])

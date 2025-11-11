from datetime import datetime

from fortytwo.request.parameter.parameter import Filter


class LocationFilter:
    """
    Filter class specifically for location resources with all supported 42 API filters.
    """

    @staticmethod
    def by_id(location_id: str | int) -> Filter:
        """
        Filter locations by ID.

        Args:
            location_id (Union[str, int]): The location ID to filter by.
        """
        return Filter("id", [location_id])

    @staticmethod
    def by_user_id(user_id: str | int) -> Filter:
        """
        Filter locations by user ID.

        Args:
            user_id (Union[str, int]): The user ID to filter by.
        """
        return Filter("user_id", [user_id])

    @staticmethod
    def by_begin_at(begin_at: str | datetime) -> Filter:
        """
        Filter locations by begin date.

        Args:
            begin_at (Union[str, datetime]): The begin date to filter by (ISO format string or datetime object).
        """
        return Filter("begin_at", [begin_at])

    @staticmethod
    def by_end_at(end_at: str | datetime) -> Filter:
        """
        Filter locations by end date.

        Args:
            end_at (Union[str, datetime]): The end date to filter by (ISO format string or datetime object).
        """
        return Filter("end_at", [end_at])

    @staticmethod
    def by_primary(primary: str | bool) -> Filter:
        """
        Filter locations by primary status.

        Args:
            primary (Union[str, bool]): The primary status to filter by.
        """
        return Filter("primary", [str(primary).lower()])

    @staticmethod
    def by_host(host: str) -> Filter:
        """
        Filter locations by host.

        Args:
            host (str): The host to filter by.
        """
        return Filter("host", [host])

    @staticmethod
    def by_campus_id(campus_id: str | int) -> Filter:
        """
        Filter locations by campus ID.

        Args:
            campus_id (Union[str, int]): The campus ID to filter by.
        """
        return Filter("campus_id", [campus_id])

    @staticmethod
    def active_only() -> Filter:
        """
        Filter only active locations.
        """
        return Filter("active", ["true"])

    @staticmethod
    def inactive_only() -> Filter:
        """
        Filter only inactive locations.
        """
        return Filter("inactive", ["true"])

    @staticmethod
    def future_only() -> Filter:
        """
        Filter only future locations.
        """
        return Filter("future", ["true"])

    @staticmethod
    def ended_only() -> Filter:
        """
        Filter only ended locations.
        """
        return Filter("end", ["true"])

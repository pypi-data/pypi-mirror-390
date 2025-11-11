from datetime import datetime

from fortytwo.request.parameter.parameter import Range


class LocationRange:
    """
    Range class specifically for location resources with all supported 42 API range fields.
    """

    @staticmethod
    def id_range(min_id: str | int | None = None, max_id: str | int | None = None) -> Range:
        """
        Filter locations by ID range.

        Args:
            min_id (Union[str, int], optional): Minimum ID value.
            max_id (Union[str, int], optional): Maximum ID value.
        """
        return Range("id", [min_id, max_id])

    @staticmethod
    def user_id_range(
        min_user_id: str | int | None = None, max_user_id: str | int | None = None
    ) -> Range:
        """
        Filter locations by user ID range.

        Args:
            min_user_id (Union[str, int], optional): Minimum user ID value.
            max_user_id (Union[str, int], optional): Maximum user ID value.
        """
        return Range("user_id", [min_user_id, max_user_id])

    @staticmethod
    def begin_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter locations by begin date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("begin_at", [start_date, end_date])

    @staticmethod
    def end_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter locations by end date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("end_at", [start_date, end_date])

    @staticmethod
    def primary_range(min_primary: str | None = None, max_primary: str | None = None) -> Range:
        """
        Filter locations by primary range.

        Args:
            min_primary (str, optional): Minimum primary value.
            max_primary (str, optional): Maximum primary value.
        """
        return Range("primary", [min_primary, max_primary])

    @staticmethod
    def host_range(min_host: str | None = None, max_host: str | None = None) -> Range:
        """
        Filter locations by host range (alphabetical).

        Args:
            min_host (str, optional): Minimum host value.
            max_host (str, optional): Maximum host value.
        """
        return Range("host", [min_host, max_host])

    @staticmethod
    def campus_id_range(
        min_campus_id: str | int | None = None, max_campus_id: str | int | None = None
    ) -> Range:
        """
        Filter locations by campus ID range.

        Args:
            min_campus_id (Union[str, int], optional): Minimum campus ID value.
            max_campus_id (Union[str, int], optional): Maximum campus ID value.
        """
        return Range("campus_id", [min_campus_id, max_campus_id])

from datetime import datetime

from fortytwo.request.parameter.parameter import Range


class CampusUserRange:
    """
    Range class specifically for campus user resources with all supported 42 API range options.
    """

    @staticmethod
    def id_range(min_id: str | int | None = None, max_id: str | int | None = None) -> Range:
        """
        Filter campus users by ID range.

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
        Filter campus users by user ID range.

        Args:
            min_user_id (Union[str, int], optional): Minimum user ID value.
            max_user_id (Union[str, int], optional): Maximum user ID value.
        """
        return Range("user_id", [min_user_id, max_user_id])

    @staticmethod
    def campus_id_range(
        min_campus_id: str | int | None = None, max_campus_id: str | int | None = None
    ) -> Range:
        """
        Filter campus users by campus ID range.

        Args:
            min_campus_id (Union[str, int], optional): Minimum campus ID value.
            max_campus_id (Union[str, int], optional): Maximum campus ID value.
        """
        return Range("campus_id", [min_campus_id, max_campus_id])

    @staticmethod
    def is_primary_range(
        min_is_primary: bool | None = None, max_is_primary: bool | None = None
    ) -> Range:
        """
        Filter campus users by primary status range.

        Args:
            min_is_primary (bool, optional): Minimum primary status.
            max_is_primary (bool, optional): Maximum primary status.
        """
        return Range("is_primary", [min_is_primary, max_is_primary])

    @staticmethod
    def created_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter campus users by creation date range.

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
        Filter campus users by update date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("updated_at", [start_date, end_date])

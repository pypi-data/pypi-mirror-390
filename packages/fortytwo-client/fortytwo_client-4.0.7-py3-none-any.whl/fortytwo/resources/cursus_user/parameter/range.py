from datetime import datetime

from fortytwo.request.parameter.parameter import Range


class CursusUserRange:
    """
    Range class specifically for cursus user resources with all supported 42 API range options.
    """

    @staticmethod
    def id_range(min_id: str | int | None = None, max_id: str | int | None = None) -> Range:
        """
        Filter cursus users by ID range.

        Args:
            min_id (Union[str, int], optional): Minimum ID value.
            max_id (Union[str, int], optional): Maximum ID value.
        """
        return Range("id", [min_id, max_id])

    @staticmethod
    def cursus_id_range(
        min_cursus_id: str | int | None = None, max_cursus_id: str | int | None = None
    ) -> Range:
        """
        Filter cursus users by cursus ID range.

        Args:
            min_cursus_id (Union[str, int], optional): Minimum cursus ID value.
            max_cursus_id (Union[str, int], optional): Maximum cursus ID value.
        """
        return Range("cursus_id", [min_cursus_id, max_cursus_id])

    @staticmethod
    def user_id_range(
        min_user_id: str | int | None = None, max_user_id: str | int | None = None
    ) -> Range:
        """
        Filter cursus users by user ID range.

        Args:
            min_user_id (Union[str, int], optional): Minimum user ID value.
            max_user_id (Union[str, int], optional): Maximum user ID value.
        """
        return Range("user_id", [min_user_id, max_user_id])

    @staticmethod
    def created_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter cursus users by creation date range.

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
        Filter cursus users by update date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("updated_at", [start_date, end_date])

    @staticmethod
    def end_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter cursus users by end date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("end_at", [start_date, end_date])

    @staticmethod
    def begin_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter cursus users by begin date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("begin_at", [start_date, end_date])

    @staticmethod
    def has_coalition_range(
        min_has_coalition: bool | None = None, max_has_coalition: bool | None = None
    ) -> Range:
        """
        Filter cursus users by coalition status range.

        Args:
            min_has_coalition (bool, optional): Minimum coalition status.
            max_has_coalition (bool, optional): Maximum coalition status.
        """
        return Range("has_coalition", [min_has_coalition, max_has_coalition])

    @staticmethod
    def blackholed_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter cursus users by blackhole date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("blackholed_at", [start_date, end_date])

    @staticmethod
    def level_range(
        min_level: str | float | None = None, max_level: str | float | None = None
    ) -> Range:
        """
        Filter cursus users by level range.

        Args:
            min_level (Union[str, float], optional): Minimum level value.
            max_level (Union[str, float], optional): Maximum level value.
        """
        return Range("level", [min_level, max_level])

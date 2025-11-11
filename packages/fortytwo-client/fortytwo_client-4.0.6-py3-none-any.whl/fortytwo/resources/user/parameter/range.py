from datetime import datetime

from fortytwo.request.parameter.parameter import Range


class UserRange:
    """
    Range class specifically for user resources with all supported 42 API range fields.
    """

    @staticmethod
    def id_range(min_id: str | int | None = None, max_id: str | int | None = None) -> Range:
        """
        Filter users by ID range.

        Args:
            min_id (Union[str, int], optional): Minimum ID value.
            max_id (Union[str, int], optional): Maximum ID value.
        """
        return Range("id", [min_id, max_id])

    @staticmethod
    def login_range(min_login: str | None = None, max_login: str | None = None) -> Range:
        """
        Filter users by login range (alphabetical).

        Args:
            min_login (str, optional): Minimum login value.
            max_login (str, optional): Maximum login value.
        """
        return Range("login", [min_login, max_login])

    @staticmethod
    def email_range(min_email: str | None = None, max_email: str | None = None) -> Range:
        """
        Filter users by email range (alphabetical).

        Args:
            min_email (str, optional): Minimum email value.
            max_email (str, optional): Maximum email value.
        """
        return Range("email", [min_email, max_email])

    @staticmethod
    def created_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter users by creation date range.

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
        Filter users by update date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("updated_at", [start_date, end_date])

    @staticmethod
    def pool_year_range(
        min_year: str | int | None = None, max_year: str | int | None = None
    ) -> Range:
        """
        Filter users by pool year range.

        Args:
            min_year (Union[str, int], optional): Minimum pool year.
            max_year (Union[str, int], optional): Maximum pool year.
        """
        return Range("pool_year", [min_year, max_year])

    @staticmethod
    def pool_month_range(
        min_month: str | int | None = None, max_month: str | int | None = None
    ) -> Range:
        """
        Filter users by pool month range.

        Args:
            min_month (Union[str, int], optional): Minimum pool month.
            max_month (Union[str, int], optional): Maximum pool month.
        """
        return Range("pool_month", [min_month, max_month])

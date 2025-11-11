from datetime import datetime

from fortytwo.request.parameter.parameter import Filter


class UserFilter:
    """
    Filter class specifically for user resources with all supported 42 API filters.
    """

    @staticmethod
    def by_id(user_id: str | int) -> Filter:
        """
        Filter users by ID.

        Args:
            user_id (Union[str, int]): The user ID to filter by.
        """
        return Filter("id", [user_id])

    @staticmethod
    def by_login(login: str) -> Filter:
        """
        Filter users by login.

        Args:
            login (str): The login to filter by.
        """
        return Filter("login", [login])

    @staticmethod
    def by_email(email: str) -> Filter:
        """
        Filter users by email.

        Args:
            email (str): The email to filter by.
        """
        return Filter("email", [email])

    @staticmethod
    def by_created_at(created_at: str | datetime) -> Filter:
        """
        Filter users by creation date.

        Args:
            created_at (Union[str, datetime]): The creation date to filter by (ISO format string or datetime object).
        """
        return Filter("created_at", [created_at])

    @staticmethod
    def by_updated_at(updated_at: str | datetime) -> Filter:
        """
        Filter users by update date.

        Args:
            updated_at (Union[str, datetime]): The update date to filter by (ISO format string or datetime object).
        """
        return Filter("updated_at", [updated_at])

    @staticmethod
    def by_pool_year(year: str | int) -> Filter:
        """
        Filter users by pool year.

        Args:
            year (Union[str, int]): The pool year to filter by.
        """
        return Filter("pool_year", [year])

    @staticmethod
    def by_pool_month(month: str | int) -> Filter:
        """
        Filter users by pool month.

        Args:
            month (Union[str, int]): The pool month to filter by.
        """
        return Filter("pool_month", [month])

    @staticmethod
    def by_kind(kind: str) -> Filter:
        """
        Filter users by kind (student, staff, etc.).

        Args:
            kind (str): The user kind to filter by.
        """
        return Filter("kind", [kind])

    @staticmethod
    def by_status(status: str) -> Filter:
        """
        Filter users by status.

        Args:
            status (str): The status to filter by.
        """
        return Filter("status", [status])

    @staticmethod
    def by_primary_campus_id(campus_id: str | int) -> Filter:
        """
        Filter users by primary campus ID.

        Args:
            campus_id (Union[str, int]): The campus ID to filter by.
        """
        return Filter("primary_campus_id", [campus_id])

    @staticmethod
    def by_first_name(first_name: str) -> Filter:
        """
        Filter users by first name.

        Args:
            first_name (str): The first name to filter by.
        """
        return Filter("first_name", [first_name])

    @staticmethod
    def by_last_name(last_name: str) -> Filter:
        """
        Filter users by last name.

        Args:
            last_name (str): The last name to filter by.
        """
        return Filter("last_name", [last_name])

    @staticmethod
    def alumni_only() -> Filter:
        """
        Filter only alumni users.
        """
        return Filter("alumni?", ["true"])

    @staticmethod
    def non_alumni_only() -> Filter:
        """
        Filter only non-alumni users.
        """
        return Filter("alumni?", ["false"])

    @staticmethod
    def staff_only() -> Filter:
        """
        Filter only staff users.
        """
        return Filter("staff?", ["true"])

    @staticmethod
    def non_staff_only() -> Filter:
        """
        Filter only non-staff users.
        """
        return Filter("staff?", ["false"])

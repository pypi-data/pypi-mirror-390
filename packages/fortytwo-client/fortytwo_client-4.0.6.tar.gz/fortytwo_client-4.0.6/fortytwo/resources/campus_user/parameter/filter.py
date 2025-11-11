from datetime import datetime

from fortytwo.request.parameter.parameter import Filter


class CampusUserFilter:
    """
    Filter class specifically for campus user resources with all supported 42 API filters.
    """

    @staticmethod
    def by_id(campus_user_id: str | int) -> Filter:
        """
        Filter campus users by ID.

        Args:
            campus_user_id (Union[str, int]): The campus user ID to filter by.
        """
        return Filter("id", [campus_user_id])

    @staticmethod
    def by_user_id(user_id: str | int) -> Filter:
        """
        Filter campus users by user ID.

        Args:
            user_id (Union[str, int]): The user ID to filter by.
        """
        return Filter("user_id", [user_id])

    @staticmethod
    def by_campus_id(campus_id: str | int) -> Filter:
        """
        Filter campus users by campus ID.

        Args:
            campus_id (Union[str, int]): The campus ID to filter by.
        """
        return Filter("campus_id", [campus_id])

    @staticmethod
    def by_is_primary(is_primary: bool) -> Filter:
        """
        Filter campus users by primary status.

        Args:
            is_primary (bool): Whether this is the primary campus for the user.
        """
        return Filter("is_primary", [is_primary])

    @staticmethod
    def by_created_at(created_at: str | datetime) -> Filter:
        """
        Filter campus users by creation date.

        Args:
            created_at (Union[str, datetime]): The creation date to filter by (ISO format string or datetime object).
        """
        return Filter("created_at", [created_at])

    @staticmethod
    def by_updated_at(updated_at: str | datetime) -> Filter:
        """
        Filter campus users by update date.

        Args:
            updated_at (Union[str, datetime]): The update date to filter by (ISO format string or datetime object).
        """
        return Filter("updated_at", [updated_at])

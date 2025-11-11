from datetime import datetime

from fortytwo.request.parameter.parameter import Filter


class CursusUserFilter:
    """
    Filter class specifically for cursus user resources with all supported 42 API filters.
    """

    @staticmethod
    def by_id(cursus_user_id: str | int) -> Filter:
        """
        Filter cursus users by ID.

        Args:
            cursus_user_id (Union[str, int]): The cursus user ID to filter by.
        """
        return Filter("id", [cursus_user_id])

    @staticmethod
    def by_cursus_id(cursus_id: str | int) -> Filter:
        """
        Filter cursus users by cursus ID.

        Args:
            cursus_id (Union[str, int]): The cursus ID to filter by.
        """
        return Filter("cursus_id", [cursus_id])

    @staticmethod
    def by_user_id(user_id: str | int) -> Filter:
        """
        Filter cursus users by user ID.

        Args:
            user_id (Union[str, int]): The user ID to filter by.
        """
        return Filter("user_id", [user_id])

    @staticmethod
    def by_created_at(created_at: str | datetime) -> Filter:
        """
        Filter cursus users by creation date.

        Args:
            created_at (Union[str, datetime]): The creation date to filter by (ISO format string or datetime object).
        """
        return Filter("created_at", [created_at])

    @staticmethod
    def by_updated_at(updated_at: str | datetime) -> Filter:
        """
        Filter cursus users by update date.

        Args:
            updated_at (Union[str, datetime]): The update date to filter by (ISO format string or datetime object).
        """
        return Filter("updated_at", [updated_at])

    @staticmethod
    def by_end_at(end_at: str | datetime) -> Filter:
        """
        Filter cursus users by end date.

        Args:
            end_at (Union[str, datetime]): The end date to filter by (ISO format string or datetime object).
        """
        return Filter("end_at", [end_at])

    @staticmethod
    def by_begin_at(begin_at: str | datetime) -> Filter:
        """
        Filter cursus users by begin date.

        Args:
            begin_at (Union[str, datetime]): The begin date to filter by (ISO format string or datetime object).
        """
        return Filter("begin_at", [begin_at])

    @staticmethod
    def by_has_coalition(has_coalition: bool) -> Filter:
        """
        Filter cursus users by coalition status.

        Args:
            has_coalition (bool): Whether the user has a coalition.
        """
        return Filter("has_coalition", [has_coalition])

    @staticmethod
    def by_blackholed_at(blackholed_at: str | datetime) -> Filter:
        """
        Filter cursus users by blackhole date.

        Args:
            blackholed_at (Union[str, datetime]): The blackhole date to filter by (ISO format string or datetime object).
        """
        return Filter("blackholed_at", [blackholed_at])

    @staticmethod
    def by_level(level: str | float) -> Filter:
        """
        Filter cursus users by level.

        Args:
            level (Union[str, float]): The level to filter by.
        """
        return Filter("level", [level])

    @staticmethod
    def by_active(active: bool) -> Filter:
        """
        Filter cursus users by active status.

        Args:
            active (bool): Whether the cursus user is active.
        """
        return Filter("active", [active])

    @staticmethod
    def by_campus_id(campus_id: str | int) -> Filter:
        """
        Filter cursus users by campus ID.

        Args:
            campus_id (Union[str, int]): The campus ID to filter by.
        """
        return Filter("campus_id", [campus_id])

    @staticmethod
    def by_end(end: bool) -> Filter:
        """
        Filter cursus users by end status.

        Args:
            end (bool): Whether the cursus has ended.
        """
        return Filter("end", [end])

    @staticmethod
    def by_future(future: bool) -> Filter:
        """
        Filter cursus users by future status.

        Args:
            future (bool): Whether the cursus is in the future.
        """
        return Filter("future", [future])

    @staticmethod
    def by_blackholed(blackholed: bool) -> Filter:
        """
        Filter cursus users by blackholed status.

        Args:
            blackholed (bool): Whether the user is blackholed.
        """
        return Filter("blackholed", [blackholed])

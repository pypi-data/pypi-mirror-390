from datetime import datetime

from fortytwo.request.parameter.parameter import Filter


class ProjectUserFilter:
    """
    Filter class specifically for project_user resources with all supported 42 API filters.
    """

    @staticmethod
    def by_id(project_user_id: str | int) -> Filter:
        """
        Filter project_users by ID.

        Args:
            project_user_id (Union[str, int]): The project_user ID to filter by.
        """
        return Filter("id", [project_user_id])

    @staticmethod
    def by_project_id(project_id: str | int) -> Filter:
        """
        Filter project_users by project ID.

        Args:
            project_id (Union[str, int]): The project ID to filter by.
        """
        return Filter("project_id", [project_id])

    @staticmethod
    def by_user_id(user_id: str | int) -> Filter:
        """
        Filter project_users by user ID.

        Args:
            user_id (Union[str, int]): The user ID to filter by.
        """
        return Filter("user_id", [user_id])

    @staticmethod
    def by_created_at(created_at: str | datetime) -> Filter:
        """
        Filter project_users by creation date.

        Args:
            created_at (Union[str, datetime]): The creation date to filter by (ISO format string or datetime object).
        """
        return Filter("created_at", [created_at])

    @staticmethod
    def by_updated_at(updated_at: str | datetime) -> Filter:
        """
        Filter project_users by update date.

        Args:
            updated_at (Union[str, datetime]): The update date to filter by (ISO format string or datetime object).
        """
        return Filter("updated_at", [updated_at])

    @staticmethod
    def by_occurrence(occurrence: str | int) -> Filter:
        """
        Filter project_users by occurrence.

        Args:
            occurrence (Union[str, int]): The occurrence to filter by.
        """
        return Filter("occurrence", [occurrence])

    @staticmethod
    def by_final_mark(final_mark: str | int) -> Filter:
        """
        Filter project_users by final mark.

        Args:
            final_mark (Union[str, int]): The final mark to filter by.
        """
        return Filter("final_mark", [final_mark])

    @staticmethod
    def by_retriable_at(retriable_at: str | datetime) -> Filter:
        """
        Filter project_users by retriable date.

        Args:
            retriable_at (Union[str, datetime]): The retriable date to filter by (ISO format string or datetime object).
        """
        return Filter("retriable_at", [retriable_at])

    @staticmethod
    def by_marked_at(marked_at: str | datetime) -> Filter:
        """
        Filter project_users by marked date.

        Args:
            marked_at (Union[str, datetime]): The marked date to filter by (ISO format string or datetime object).
        """
        return Filter("marked_at", [marked_at])

    @staticmethod
    def by_status(status: str) -> Filter:
        """
        Filter project_users by status.

        Args:
            status (str): The status to filter by.
        """
        return Filter("status", [status])

    @staticmethod
    def by_cursus(cursus: str | int) -> Filter:
        """
        Filter project_users by cursus.

        Args:
            cursus (Union[str, int]): The cursus to filter by.
        """
        return Filter("cursus", [cursus])

    @staticmethod
    def by_campus(campus: str | int) -> Filter:
        """
        Filter project_users by campus.

        Args:
            campus (Union[str, int]): The campus to filter by.
        """
        return Filter("campus", [campus])

    @staticmethod
    def retriable_only() -> Filter:
        """
        Filter only retriable project_users.
        """
        return Filter("retriable", ["true"])

    @staticmethod
    def non_retriable_only() -> Filter:
        """
        Filter only non-retriable project_users.
        """
        return Filter("retriable", ["false"])

    @staticmethod
    def marked_only() -> Filter:
        """
        Filter only marked project_users.
        """
        return Filter("marked", ["true"])

    @staticmethod
    def non_marked_only() -> Filter:
        """
        Filter only non-marked project_users.
        """
        return Filter("marked", ["false"])

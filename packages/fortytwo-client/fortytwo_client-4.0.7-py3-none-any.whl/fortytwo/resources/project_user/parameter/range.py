from datetime import datetime

from fortytwo.request.parameter.parameter import Range


class ProjectUserRange:
    """
    Range class specifically for project_user resources with all supported 42 API range fields.
    """

    @staticmethod
    def id_range(min_id: str | int | None = None, max_id: str | int | None = None) -> Range:
        """
        Filter project_users by ID range.

        Args:
            min_id (Union[str, int], optional): Minimum ID value.
            max_id (Union[str, int], optional): Maximum ID value.
        """
        return Range("id", [min_id, max_id])

    @staticmethod
    def project_id_range(
        min_project_id: str | int | None = None, max_project_id: str | int | None = None
    ) -> Range:
        """
        Filter project_users by project ID range.

        Args:
            min_project_id (Union[str, int], optional): Minimum project ID value.
            max_project_id (Union[str, int], optional): Maximum project ID value.
        """
        return Range("project_id", [min_project_id, max_project_id])

    @staticmethod
    def user_id_range(
        min_user_id: str | int | None = None, max_user_id: str | int | None = None
    ) -> Range:
        """
        Filter project_users by user ID range.

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
        Filter project_users by creation date range.

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
        Filter project_users by update date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("updated_at", [start_date, end_date])

    @staticmethod
    def occurrence_range(
        min_occurrence: str | int | None = None, max_occurrence: str | int | None = None
    ) -> Range:
        """
        Filter project_users by occurrence range.

        Args:
            min_occurrence (Union[str, int], optional): Minimum occurrence value.
            max_occurrence (Union[str, int], optional): Maximum occurrence value.
        """
        return Range("occurrence", [min_occurrence, max_occurrence])

    @staticmethod
    def final_mark_range(
        min_final_mark: str | int | None = None, max_final_mark: str | int | None = None
    ) -> Range:
        """
        Filter project_users by final mark range.

        Args:
            min_final_mark (Union[str, int], optional): Minimum final mark value.
            max_final_mark (Union[str, int], optional): Maximum final mark value.
        """
        return Range("final_mark", [min_final_mark, max_final_mark])

    @staticmethod
    def retriable_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter project_users by retriable date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("retriable_at", [start_date, end_date])

    @staticmethod
    def marked_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter project_users by marked date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("marked_at", [start_date, end_date])

    @staticmethod
    def status_range(min_status: str | None = None, max_status: str | None = None) -> Range:
        """
        Filter project_users by status range (alphabetical).

        Args:
            min_status (str, optional): Minimum status value.
            max_status (str, optional): Maximum status value.
        """
        values = []
        if min_status is not None:
            values.append(min_status)
        if max_status is not None:
            if min_status is None:
                values.append("")
            values.append(max_status)
        return Range("status", values)

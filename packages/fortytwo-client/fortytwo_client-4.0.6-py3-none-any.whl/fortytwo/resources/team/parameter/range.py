from datetime import datetime

from fortytwo.request.parameter.parameter import Range


class TeamRange:
    """
    Range class specifically for team resources with all supported 42 API range options.
    """

    @staticmethod
    def id_range(min_id: str | int | None = None, max_id: str | int | None = None) -> Range:
        """
        Filter teams by ID range.

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
        Filter teams by project ID range.

        Args:
            min_project_id (Union[str, int], optional): Minimum project ID value.
            max_project_id (Union[str, int], optional): Maximum project ID value.
        """
        return Range("project_id", [min_project_id, max_project_id])

    @staticmethod
    def name_range(min_name: str | None = None, max_name: str | None = None) -> Range:
        """
        Filter teams by name range (alphabetical).

        Args:
            min_name (str, optional): Minimum name value.
            max_name (str, optional): Maximum name value.
        """
        return Range("name", [min_name, max_name])

    @staticmethod
    def created_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter teams by creation date range.

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
        Filter teams by update date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("updated_at", [start_date, end_date])

    @staticmethod
    def locked_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter teams by locked date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("locked_at", [start_date, end_date])

    @staticmethod
    def closed_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter teams by closed date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("closed_at", [start_date, end_date])

    @staticmethod
    def final_mark_range(
        min_final_mark: str | int | None = None, max_final_mark: str | int | None = None
    ) -> Range:
        """
        Filter teams by final mark range.

        Args:
            min_final_mark (Union[str, int], optional): Minimum final mark value.
            max_final_mark (Union[str, int], optional): Maximum final mark value.
        """
        return Range("final_mark", [min_final_mark, max_final_mark])

    @staticmethod
    def repo_url_range(min_repo_url: str | None = None, max_repo_url: str | None = None) -> Range:
        """
        Filter teams by repository URL range (alphabetical).

        Args:
            min_repo_url (str, optional): Minimum repository URL value.
            max_repo_url (str, optional): Maximum repository URL value.
        """
        return Range("repo_url", [min_repo_url, max_repo_url])

    @staticmethod
    def repo_uuid_range(
        min_repo_uuid: str | None = None, max_repo_uuid: str | None = None
    ) -> Range:
        """
        Filter teams by repository UUID range (alphabetical).

        Args:
            min_repo_uuid (str, optional): Minimum repository UUID value.
            max_repo_uuid (str, optional): Maximum repository UUID value.
        """
        return Range("repo_uuid", [min_repo_uuid, max_repo_uuid])

    @staticmethod
    def deadline_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter teams by deadline date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("deadline_at", [start_date, end_date])

    @staticmethod
    def terminating_at_range(
        start_date: str | datetime | None = None, end_date: str | datetime | None = None
    ) -> Range:
        """
        Filter teams by terminating date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("terminating_at", [start_date, end_date])

    @staticmethod
    def project_session_id_range(
        min_project_session_id: str | int | None = None,
        max_project_session_id: str | int | None = None,
    ) -> Range:
        """
        Filter teams by project session ID range.

        Args:
            min_project_session_id (Union[str, int], optional): Minimum project session ID value.
            max_project_session_id (Union[str, int], optional): Maximum project session ID value.
        """
        return Range("project_session_id", [min_project_session_id, max_project_session_id])

    @staticmethod
    def status_range(min_status: str | None = None, max_status: str | None = None) -> Range:
        """
        Filter teams by status range (alphabetical).

        Args:
            min_status (str, optional): Minimum status value.
            max_status (str, optional): Maximum status value.
        """
        return Range("status", [min_status, max_status])

from datetime import datetime

from fortytwo.request.parameter.parameter import Filter


class TeamFilter:
    """
    Filter class specifically for team resources with all supported 42 API filters.
    """

    @staticmethod
    def by_id(team_id: str | int) -> Filter:
        """
        Filter teams by ID.

        Args:
            team_id (Union[str, int]): The team ID to filter by.
        """
        return Filter("id", [team_id])

    @staticmethod
    def by_project_id(project_id: str | int) -> Filter:
        """
        Filter teams by project ID.

        Args:
            project_id (Union[str, int]): The project ID to filter by.
        """
        return Filter("project_id", [project_id])

    @staticmethod
    def by_name(name: str) -> Filter:
        """
        Filter teams by name.

        Args:
            name (str): The team name to filter by.
        """
        return Filter("name", [name])

    @staticmethod
    def by_created_at(created_at: str | datetime) -> Filter:
        """
        Filter teams by creation date.

        Args:
            created_at (Union[str, datetime]): The creation date to filter by (ISO format string or datetime object).
        """
        return Filter("created_at", [created_at])

    @staticmethod
    def by_updated_at(updated_at: str | datetime) -> Filter:
        """
        Filter teams by update date.

        Args:
            updated_at (Union[str, datetime]): The update date to filter by (ISO format string or datetime object).
        """
        return Filter("updated_at", [updated_at])

    @staticmethod
    def by_locked_at(locked_at: str | datetime) -> Filter:
        """
        Filter teams by locked date.

        Args:
            locked_at (Union[str, datetime]): The locked date to filter by (ISO format string or datetime object).
        """
        return Filter("locked_at", [locked_at])

    @staticmethod
    def by_closed_at(closed_at: str | datetime) -> Filter:
        """
        Filter teams by closed date.

        Args:
            closed_at (Union[str, datetime]): The closed date to filter by (ISO format string or datetime object).
        """
        return Filter("closed_at", [closed_at])

    @staticmethod
    def by_final_mark(final_mark: str | int) -> Filter:
        """
        Filter teams by final mark.

        Args:
            final_mark (Union[str, int]): The final mark to filter by.
        """
        return Filter("final_mark", [final_mark])

    @staticmethod
    def by_repo_url(repo_url: str) -> Filter:
        """
        Filter teams by repository URL.

        Args:
            repo_url (str): The repository URL to filter by.
        """
        return Filter("repo_url", [repo_url])

    @staticmethod
    def by_repo_uuid(repo_uuid: str) -> Filter:
        """
        Filter teams by repository UUID.

        Args:
            repo_uuid (str): The repository UUID to filter by.
        """
        return Filter("repo_uuid", [repo_uuid])

    @staticmethod
    def by_deadline_at(deadline_at: str | datetime) -> Filter:
        """
        Filter teams by deadline date.

        Args:
            deadline_at (Union[str, datetime]): The deadline date to filter by (ISO format string or datetime object).
        """
        return Filter("deadline_at", [deadline_at])

    @staticmethod
    def by_terminating_at(terminating_at: str | datetime) -> Filter:
        """
        Filter teams by terminating date.

        Args:
            terminating_at (Union[str, datetime]): The terminating date to filter by (ISO format string or datetime object).
        """
        return Filter("terminating_at", [terminating_at])

    @staticmethod
    def by_project_session_id(project_session_id: str | int) -> Filter:
        """
        Filter teams by project session ID.

        Args:
            project_session_id (Union[str, int]): The project session ID to filter by.
        """
        return Filter("project_session_id", [project_session_id])

    @staticmethod
    def by_status(status: str) -> Filter:
        """
        Filter teams by status.

        Args:
            status (str): The status to filter by.
        """
        return Filter("status", [status])

    @staticmethod
    def by_cursus(cursus: str | bool) -> Filter:
        """
        Filter teams by cursus.

        Args:
            cursus (Union[str, bool]): The cursus to filter by.
        """
        return Filter("cursus", [str(cursus).lower() if isinstance(cursus, bool) else cursus])

    @staticmethod
    def by_active_cursus(active_cursus: str | bool) -> Filter:
        """
        Filter teams by active cursus.

        Args:
            active_cursus (Union[str, bool]): The active cursus to filter by.
        """
        return Filter(
            "active_cursus",
            [str(active_cursus).lower() if isinstance(active_cursus, bool) else active_cursus],
        )

    @staticmethod
    def by_campus(campus: str | bool) -> Filter:
        """
        Filter teams by campus.

        Args:
            campus (Union[str, bool]): The campus to filter by.
        """
        return Filter("campus", [str(campus).lower() if isinstance(campus, bool) else campus])

    @staticmethod
    def by_primary_campus(primary_campus: str | bool) -> Filter:
        """
        Filter teams by primary campus.

        Args:
            primary_campus (Union[str, bool]): The primary campus to filter by.
        """
        return Filter(
            "primary_campus",
            [str(primary_campus).lower() if isinstance(primary_campus, bool) else primary_campus],
        )

    @staticmethod
    def by_locked(locked: str | bool) -> Filter:
        """
        Filter teams by locked status.

        Args:
            locked (Union[str, bool]): The locked status to filter by.
        """
        return Filter("locked", [str(locked).lower()])

    @staticmethod
    def by_closed(closed: str | bool) -> Filter:
        """
        Filter teams by closed status.

        Args:
            closed (Union[str, bool]): The closed status to filter by.
        """
        return Filter("closed", [str(closed).lower()])

    @staticmethod
    def by_deadline(deadline: str | bool) -> Filter:
        """
        Filter teams by deadline.

        Args:
            deadline (Union[str, bool]): The deadline to filter by.
        """
        return Filter(
            "deadline", [str(deadline).lower() if isinstance(deadline, bool) else deadline]
        )

    @staticmethod
    def by_terminating(terminating: str | bool) -> Filter:
        """
        Filter teams by terminating status.

        Args:
            terminating (Union[str, bool]): The terminating status to filter by.
        """
        return Filter(
            "terminating",
            [str(terminating).lower() if isinstance(terminating, bool) else terminating],
        )

    @staticmethod
    def by_with_mark(with_mark: str | bool) -> Filter:
        """
        Filter teams by with_mark status.

        Args:
            with_mark (Union[str, bool]): The with_mark status to filter by.
        """
        return Filter("with_mark", [str(with_mark).lower()])

from fortytwo.request.parameter.parameter import Sort, SortDirection


class TeamSort:
    """
    Sort class specifically for team resources with all supported 42 API sort options.
    """

    @staticmethod
    def by_id(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort teams by ID (default descending).

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("id", direction)])

    @staticmethod
    def by_project_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort teams by project ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("project_id", direction)])

    @staticmethod
    def by_name(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort teams by name.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("name", direction)])

    @staticmethod
    def by_created_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort teams by creation date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("created_at", direction)])

    @staticmethod
    def by_updated_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort teams by update date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("updated_at", direction)])

    @staticmethod
    def by_locked_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort teams by locked date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("locked_at", direction)])

    @staticmethod
    def by_closed_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort teams by closed date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("closed_at", direction)])

    @staticmethod
    def by_final_mark(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort teams by final mark.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("final_mark", direction)])

    @staticmethod
    def by_repo_url(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort teams by repository URL.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("repo_url", direction)])

    @staticmethod
    def by_repo_uuid(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort teams by repository UUID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("repo_uuid", direction)])

    @staticmethod
    def by_deadline_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort teams by deadline date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("deadline_at", direction)])

    @staticmethod
    def by_terminating_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort teams by terminating date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("terminating_at", direction)])

    @staticmethod
    def by_project_session_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort teams by project session ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("project_session_id", direction)])

    @staticmethod
    def by_status(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort teams by status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("status", direction)])

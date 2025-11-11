from fortytwo.request.parameter.parameter import Sort, SortDirection


class UserSort:
    """
    Sort class specifically for user resources with all supported 42 API sort fields.
    """

    @staticmethod
    def by_id(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by ID (default descending).

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("id", direction)])

    @staticmethod
    def by_login(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by login.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("login", direction)])

    @staticmethod
    def by_email(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by email.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("email", direction)])

    @staticmethod
    def by_created_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by creation date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("created_at", direction)])

    @staticmethod
    def by_updated_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by update date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("updated_at", direction)])

    @staticmethod
    def by_first_name(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by first name.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("first_name", direction)])

    @staticmethod
    def by_last_name(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by last name.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("last_name", direction)])

    @staticmethod
    def by_pool_year(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by pool year.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("pool_year", direction)])

    @staticmethod
    def by_pool_month(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by pool month.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("pool_month", direction)])

    @staticmethod
    def by_kind(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by user kind.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("kind", direction)])

    @staticmethod
    def by_status(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("status", direction)])

    @staticmethod
    def by_last_seen_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by last seen date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("last_seen_at", direction)])

    @staticmethod
    def by_alumnized_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by alumnized date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("alumnized_at", direction)])

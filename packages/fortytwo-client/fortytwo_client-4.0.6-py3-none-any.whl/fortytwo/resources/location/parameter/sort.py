from fortytwo.request.parameter.parameter import Sort, SortDirection


class LocationSort:
    """
    Sort class specifically for location resources with all supported 42 API sort fields.
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
    def by_user_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by user ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("user_id", direction)])

    @staticmethod
    def by_begin_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by begin date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("begin_at", direction)])

    @staticmethod
    def by_end_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by end date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("end_at", direction)])

    @staticmethod
    def by_primary(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by primary status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("primary", direction)])

    @staticmethod
    def by_host(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by host.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("host", direction)])

    @staticmethod
    def by_campus_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by campus ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("campus_id", direction)])

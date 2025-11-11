from fortytwo.request.parameter.parameter import Sort, SortDirection


class CampusUserSort:
    """
    Sort class specifically for campus user resources with all supported 42 API sort options.
    """

    @staticmethod
    def by_id(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort campus users by ID (default descending).

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("id", direction)])

    @staticmethod
    def by_user_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort campus users by user ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("user_id", direction)])

    @staticmethod
    def by_campus_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort campus users by campus ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("campus_id", direction)])

    @staticmethod
    def by_is_primary(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort campus users by primary status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("is_primary", direction)])

    @staticmethod
    def by_created_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort campus users by creation date (default descending).

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("created_at", direction)])

    @staticmethod
    def by_updated_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort campus users by update date (default descending).

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("updated_at", direction)])

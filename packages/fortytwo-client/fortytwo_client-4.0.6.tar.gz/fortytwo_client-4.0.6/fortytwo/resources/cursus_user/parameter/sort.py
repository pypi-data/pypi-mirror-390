from fortytwo.request.parameter.parameter import Sort, SortDirection


class CursusUserSort:
    """
    Sort class specifically for cursus user resources with all supported 42 API sort options.
    """

    @staticmethod
    def by_id(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort cursus users by ID (default descending).

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("id", direction)])

    @staticmethod
    def by_cursus_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort cursus users by cursus ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("cursus_id", direction)])

    @staticmethod
    def by_user_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort cursus users by user ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("user_id", direction)])

    @staticmethod
    def by_created_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort cursus users by creation date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("created_at", direction)])

    @staticmethod
    def by_updated_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort cursus users by update date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("updated_at", direction)])

    @staticmethod
    def by_end_at(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort cursus users by end date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("end_at", direction)])

    @staticmethod
    def by_begin_at(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort cursus users by begin date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("begin_at", direction)])

    @staticmethod
    def by_has_coalition(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort cursus users by coalition status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("has_coalition", direction)])

    @staticmethod
    def by_blackholed_at(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort cursus users by blackhole date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("blackholed_at", direction)])

    @staticmethod
    def by_level(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort cursus users by level (default descending).

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("level", direction)])

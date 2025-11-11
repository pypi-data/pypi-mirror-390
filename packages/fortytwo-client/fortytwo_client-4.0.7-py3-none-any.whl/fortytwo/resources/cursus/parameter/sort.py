from fortytwo.request.parameter.parameter import Sort, SortDirection


class CursusSort:
    """
    Sort class specifically for cursus resources with all supported 42 API sort options.
    """

    @staticmethod
    def by_id(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort cursuses by ID (default descending).

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("id", direction)])

    @staticmethod
    def by_name(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort cursuses by name.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("name", direction)])

    @staticmethod
    def by_created_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort cursuses by created date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("created_at", direction)])

    @staticmethod
    def by_updated_at(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort cursuses by updated date.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("updated_at", direction)])

    @staticmethod
    def by_slug(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort cursuses by slug.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("slug", direction)])

    @staticmethod
    def by_kind(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort cursuses by kind.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("kind", direction)])

    @staticmethod
    def by_restricted(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort cursuses by restricted status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("restricted", direction)])

    @staticmethod
    def by_is_subscriptable(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort cursuses by subscriptable status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("is_subscriptable", direction)])

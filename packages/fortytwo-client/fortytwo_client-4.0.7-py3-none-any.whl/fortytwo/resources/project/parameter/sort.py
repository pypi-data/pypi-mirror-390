from fortytwo.request.parameter.parameter import Sort, SortDirection


class ProjectSort:
    """
    Sort class specifically for project resources with all supported 42 API sort fields.
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
    def by_name(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by name.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("name", direction)])

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
    def by_visible(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by visibility status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("visible", direction)])

    @staticmethod
    def by_exam(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by exam status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("exam", direction)])

    @staticmethod
    def by_parent_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by parent ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("parent_id", direction)])

    @staticmethod
    def by_slug(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by slug.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("slug", direction)])

    @staticmethod
    def by_inherited_team(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by inherited team status.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("inherited_team", direction)])

    @staticmethod
    def by_position(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by position.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("position", direction)])

    @staticmethod
    def by_has_git(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by git availability.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("has_git", direction)])

    @staticmethod
    def by_has_mark(direction: SortDirection = SortDirection.DESCENDING) -> Sort:
        """
        Sort by mark availability.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("has_mark", direction)])

    @staticmethod
    def by_repository(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by repository.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("repository", direction)])

    @staticmethod
    def by_git_id(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by git ID.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("git_id", direction)])

    @staticmethod
    def by_cached_repository_path(direction: SortDirection = SortDirection.ASCENDING) -> Sort:
        """
        Sort by cached repository path.

        Args:
            direction (SortDirection): Sort direction.
        """
        return Sort([("cached_repository_path", direction)])

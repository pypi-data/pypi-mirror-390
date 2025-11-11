from datetime import datetime

from fortytwo.request.parameter.parameter import Filter


class ProjectFilter:
    """
    Filter class specifically for project resources with all supported 42 API filters.
    """

    @staticmethod
    def by_id(project_id: str | int) -> Filter:
        """
        Filter projects by ID.

        Args:
            project_id (Union[str, int]): The project ID to filter by.
        """
        return Filter("id", [project_id])

    @staticmethod
    def by_name(name: str) -> Filter:
        """
        Filter projects by name.

        Args:
            name (str): The project name to filter by.
        """
        return Filter("name", [name])

    @staticmethod
    def by_created_at(created_at: str | datetime) -> Filter:
        """
        Filter projects by creation date.

        Args:
            created_at (Union[str, datetime]): The creation date to filter by (ISO format string or datetime object).
        """
        return Filter("created_at", [created_at])

    @staticmethod
    def by_updated_at(updated_at: str | datetime) -> Filter:
        """
        Filter projects by update date.

        Args:
            updated_at (Union[str, datetime]): The update date to filter by (ISO format string or datetime object).
        """
        return Filter("updated_at", [updated_at])

    @staticmethod
    def by_visible(visible: str | bool) -> Filter:
        """
        Filter projects by visibility status.

        Args:
            visible (Union[str, bool]): The visibility status to filter by.
        """
        return Filter("visible", [str(visible).lower()])

    @staticmethod
    def by_exam(exam: str | bool) -> Filter:
        """
        Filter projects by exam status.

        Args:
            exam (Union[str, bool]): The exam status to filter by.
        """
        return Filter("exam", [str(exam).lower()])

    @staticmethod
    def by_parent_id(parent_id: str | int) -> Filter:
        """
        Filter projects by parent ID.

        Args:
            parent_id (Union[str, int]): The parent ID to filter by.
        """
        return Filter("parent_id", [parent_id])

    @staticmethod
    def by_slug(slug: str) -> Filter:
        """
        Filter projects by slug.

        Args:
            slug (str): The project slug to filter by.
        """
        return Filter("slug", [slug])

    @staticmethod
    def by_inherited_team(inherited_team: str | bool) -> Filter:
        """
        Filter projects by inherited team status.

        Args:
            inherited_team (Union[str, bool]): The inherited team status to filter by.
        """
        return Filter("inherited_team", [str(inherited_team).lower()])

    @staticmethod
    def by_position(position: str | int) -> Filter:
        """
        Filter projects by position.

        Args:
            position (Union[str, int]): The position to filter by.
        """
        return Filter("position", [position])

    @staticmethod
    def by_has_git(has_git: str | bool) -> Filter:
        """
        Filter projects by git availability.

        Args:
            has_git (Union[str, bool]): The git availability status to filter by.
        """
        return Filter("has_git", [str(has_git).lower()])

    @staticmethod
    def by_has_mark(has_mark: str | bool) -> Filter:
        """
        Filter projects by mark availability.

        Args:
            has_mark (Union[str, bool]): The mark availability status to filter by.
        """
        return Filter("has_mark", [str(has_mark).lower()])

    @staticmethod
    def by_description(description: str) -> Filter:
        """
        Filter projects by description.

        Args:
            description (str): The description to filter by.
        """
        return Filter("description", [description])

    @staticmethod
    def by_difficulty(difficulty: str | int) -> Filter:
        """
        Filter projects by difficulty.

        Args:
            difficulty (Union[str, int]): The difficulty level to filter by.
        """
        return Filter("difficulty", [difficulty])

from datetime import datetime

from fortytwo.request.parameter.parameter import Range


class ProjectRange:
    """
    Range class specifically for project resources with all supported 42 API range fields.
    """

    @staticmethod
    def id_range(min_id: str | int | None = None, max_id: str | int | None = None) -> Range:
        """
        Filter projects by ID range.

        Args:
            min_id (Union[str, int], optional): Minimum ID value.
            max_id (Union[str, int], optional): Maximum ID value.
        """
        return Range("id", [min_id, max_id])

    @staticmethod
    def name_range(min_name: str | None = None, max_name: str | None = None) -> Range:
        """
        Filter projects by name range (alphabetical).

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
        Filter projects by creation date range.

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
        Filter projects by update date range.

        Args:
            start_date (Union[str, datetime], optional): Start date (ISO format string or datetime object).
            end_date (Union[str, datetime], optional): End date (ISO format string or datetime object).
        """
        return Range("updated_at", [start_date, end_date])

    @staticmethod
    def parent_id_range(
        min_parent_id: str | int | None = None, max_parent_id: str | int | None = None
    ) -> Range:
        """
        Filter projects by parent ID range.

        Args:
            min_parent_id (Union[str, int], optional): Minimum parent ID value.
            max_parent_id (Union[str, int], optional): Maximum parent ID value.
        """
        return Range("parent_id", [min_parent_id, max_parent_id])

    @staticmethod
    def slug_range(min_slug: str | None = None, max_slug: str | None = None) -> Range:
        """
        Filter projects by slug range (alphabetical).

        Args:
            min_slug (str, optional): Minimum slug value.
            max_slug (str, optional): Maximum slug value.
        """
        return Range("slug", [min_slug, max_slug])

    @staticmethod
    def position_range(
        min_position: str | int | None = None, max_position: str | int | None = None
    ) -> Range:
        """
        Filter projects by position range.

        Args:
            min_position (Union[str, int], optional): Minimum position value.
            max_position (Union[str, int], optional): Maximum position value.
        """
        return Range("position", [min_position, max_position])

    @staticmethod
    def description_range(
        min_description: str | None = None, max_description: str | None = None
    ) -> Range:
        """
        Filter projects by description range (alphabetical).

        Args:
            min_description (str, optional): Minimum description value.
            max_description (str, optional): Maximum description value.
        """
        return Range("description", [min_description, max_description])

    @staticmethod
    def difficulty_range(
        min_difficulty: str | int | None = None, max_difficulty: str | int | None = None
    ) -> Range:
        """
        Filter projects by difficulty range.

        Args:
            min_difficulty (Union[str, int], optional): Minimum difficulty value.
            max_difficulty (Union[str, int], optional): Maximum difficulty value.
        """
        return Range("difficulty", [min_difficulty, max_difficulty])

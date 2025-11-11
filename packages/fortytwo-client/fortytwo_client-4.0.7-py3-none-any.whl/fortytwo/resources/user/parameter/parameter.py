from fortytwo.request.parameter.parameter import Parameter


class UserParameter:
    """
    Parameter class specifically for user resources with all supported 42 API parameters.
    """

    @staticmethod
    def coalition_id(coalition_id: str | int) -> Parameter:
        """
        The coalition id or slug.

        Args:
            coalition_id (Union[str, int]): The coalition id or slug.
        """
        return Parameter("coalition_id", coalition_id)

    @staticmethod
    def dash_id(dash_id: str) -> Parameter:
        """
        The dash id or slug.

        Args:
            dash_id (str): The dash id or slug.
        """
        return Parameter("dash_id", dash_id)

    @staticmethod
    def event_id(event_id: str | int) -> Parameter:
        """
        The event id.

        Args:
            event_id (Union[str, int]): The event id.
        """
        return Parameter("event_id", event_id)

    @staticmethod
    def accreditation_id(accreditation_id: str | int) -> Parameter:
        """
        The accreditation id.

        Args:
            accreditation_id (Union[str, int]): The accreditation id.
        """
        return Parameter("accreditation_id", accreditation_id)

    @staticmethod
    def team_id(team_id: str | int) -> Parameter:
        """
        The team id.

        Args:
            team_id (Union[str, int]): The team id.
        """
        return Parameter("team_id", team_id)

    @staticmethod
    def project_id(project_id: str | int) -> Parameter:
        """
        The project id or slug.

        Args:
            project_id (Union[str, int]): The project id or slug.
        """
        return Parameter("project_id", project_id)

    @staticmethod
    def partnership_id(partnership_id: str | int) -> Parameter:
        """
        The partnership id or slug.

        Args:
            partnership_id (Union[str, int]): The partnership id or slug.
        """
        return Parameter("partnership_id", partnership_id)

    @staticmethod
    def expertise_id(expertise_id: str | int) -> Parameter:
        """
        The expertise id or slug.

        Args:
            expertise_id (Union[str, int]): The expertise id or slug.
        """
        return Parameter("expertise_id", expertise_id)

    @staticmethod
    def cursus_id(cursus_id: str | int) -> Parameter:
        """
        The cursus id or slug.

        Args:
            cursus_id (Union[str, int]): The cursus id or slug.
        """
        return Parameter("cursus_id", cursus_id)

    @staticmethod
    def campus_id(campus_id: str | int) -> Parameter:
        """
        The campus id or slug.

        Args:
            campus_id (Union[str, int]): The campus id or slug.
        """
        return Parameter("campus_id", campus_id)

    @staticmethod
    def achievement_id(achievement_id: str | int) -> Parameter:
        """
        The achievement id or slug.

        Args:
            achievement_id (Union[str, int]): The achievement id or slug.
        """
        return Parameter("achievement_id", achievement_id)

    @staticmethod
    def title_id(title_id: str | int) -> Parameter:
        """
        The title id or slug.

        Args:
            title_id (Union[str, int]): The title id or slug.
        """
        return Parameter("title_id", title_id)

    @staticmethod
    def quest_id(quest_id: str | int) -> Parameter:
        """
        The quest id or slug.

        Args:
            quest_id (Union[str, int]): The quest id or slug.
        """
        return Parameter("quest_id", quest_id)

    @staticmethod
    def group_id(group_id: str | int) -> Parameter:
        """
        The group id.

        Args:
            group_id (Union[str, int]): The group id.
        """
        return Parameter("group_id", group_id)

from fortytwo.request.parameter.parameter import Parameter


class TeamParameter:
    """
    Parameter class specifically for team resources with all supported 42 API parameters.
    """

    @staticmethod
    def cursus_id(cursus_id: str | int) -> Parameter:
        """
        The cursus id or slug.

        Args:
            cursus_id (Union[str, int]): The cursus id or slug.
        """
        return Parameter("cursus_id", cursus_id)

    @staticmethod
    def user_id(user_id: str | int) -> Parameter:
        """
        The user id or slug.

        Args:
            user_id (Union[str, int]): The user id or slug.
        """
        return Parameter("user_id", user_id)

    @staticmethod
    def project_id(project_id: str | int) -> Parameter:
        """
        The project id or slug.

        Args:
            project_id (Union[str, int]): The project id or slug.
        """
        return Parameter("project_id", project_id)

    @staticmethod
    def project_session_id(project_session_id: str | int) -> Parameter:
        """
        The project session id.

        Args:
            project_session_id (Union[str, int]): The project session id.
        """
        return Parameter("project_session_id", project_session_id)

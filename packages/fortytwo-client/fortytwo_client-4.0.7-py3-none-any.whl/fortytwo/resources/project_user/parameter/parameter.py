from fortytwo.request.parameter.parameter import Parameter


class ProjectUserParameter:
    """
    Parameter class specifically for project_user resources with all supported 42 API parameters.
    """

    @staticmethod
    def project_id(project_id: str | int) -> Parameter:
        """
        The project id or slug.

        Args:
            project_id (Union[str, int]): The project id or slug.
        """
        return Parameter("project_id", project_id)

    @staticmethod
    def user_id(user_id: str | int) -> Parameter:
        """
        The user id.

        Args:
            user_id (Union[str, int]): The user id.
        """
        return Parameter("user_id", user_id)

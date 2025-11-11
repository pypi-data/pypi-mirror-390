from fortytwo.request.parameter.parameter import Parameter


class ProjectParameter:
    """
    Parameter class specifically for project resources with all supported 42 API parameters.
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
    def project_id(project_id: str | int) -> Parameter:
        """
        The project id or slug.

        Args:
            project_id (Union[str, int]): The project id or slug.
        """
        return Parameter("project_id", project_id)

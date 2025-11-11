from fortytwo.request.parameter.parameter import Parameter


class CursusUserParameter:
    """
    Parameter class specifically for cursus user resources with all supported 42 API parameters.
    """

    @staticmethod
    def user_id(user_id: str | int) -> Parameter:
        """
        The user id or slug.

        Args:
            user_id (Union[str, int]): The user id or slug.
        """
        return Parameter("user_id", user_id)

    @staticmethod
    def cursus_id(cursus_id: str | int) -> Parameter:
        """
        The cursus id or slug.

        Args:
            cursus_id (Union[str, int]): The cursus id or slug.
        """
        return Parameter("cursus_id", cursus_id)

from fortytwo.request.parameter.parameter import Parameter


class CampusUserParameter:
    """
    Parameter class specifically for campus user resources with all supported 42 API parameters.
    """

    @staticmethod
    def user_id(user_id: str | int) -> Parameter:
        """
        The user id or slug.

        Args:
            user_id (Union[str, int]): The user id or slug.
        """
        return Parameter("user_id", user_id)

from fortytwo.request.parameter.parameter import Parameter


class LocationParameter:
    """
    Parameter class specifically for location resources with all supported 42 API parameters.
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
    def campus_id(campus_id: str | int) -> Parameter:
        """
        The campus id or slug.

        Args:
            campus_id (Union[str, int]): The campus id or slug.
        """
        return Parameter("campus_id", campus_id)

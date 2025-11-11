"""
Resources for fetching team data from the 42 API.
"""

from typing import Any, Self

from fortytwo.resources.resource import Resource, ResourceTemplate
from fortytwo.resources.team.team import Team


class GetTeams(Resource[list[Team]]):
    """
    Resource for fetching all teams.

    Returns a list of teams from the /teams endpoint.
    Supports pagination via parameters.
    """

    method: str = "GET"
    _url: str = "/teams"

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [Team(team) for team in response_data]


class GetTeamsByCursusId(Resource[list[Team]]):
    """
    Resource for fetching teams for a specific cursus.

    Args:
        cursus_id: The ID of the cursus to fetch teams for.
    """

    method: str = "GET"
    _url: str = "/cursus/%s/teams"

    def __init__(self: Self, cursus_id: int) -> None:
        self.cursus_id = cursus_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.cursus_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [Team(team) for team in response_data]


class GetTeamsByUserId(Resource[list[Team]]):
    """
    Resource for fetching teams for a specific user.

    Args:
        user_id: The ID of the user to fetch teams for.
    """

    method: str = "GET"
    _url: str = "/users/%s/teams"

    def __init__(self: Self, user_id: int) -> None:
        self.user_id = user_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.user_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [Team(team) for team in response_data]


class GetTeamsByProjectId(Resource[list[Team]]):
    """
    Resource for fetching teams for a specific project.

    Args:
        project_id: The ID of the project to fetch teams for.
    """

    method: str = "GET"
    _url: str = "/projects/%s/teams"

    def __init__(self: Self, project_id: int) -> None:
        self.project_id = project_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.project_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [Team(team) for team in response_data]


class GetTeamsByUserIdAndProjectId(Resource[list[Team]]):
    """
    Resource for fetching teams for a specific user and project.

    Args:
        user_id: The ID of the user to fetch teams for.
        project_id: The ID of the project to fetch teams for.
    """

    method: str = "GET"
    _url: str = "/users/%s/projects/%s/teams"

    def __init__(self: Self, user_id: int, project_id: int) -> None:
        self.user_id = user_id
        self.project_id = project_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % (self.user_id, self.project_id)

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [Team(team) for team in response_data]

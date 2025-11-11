"""
Resources for fetching project user data from the 42 API.
"""

from typing import Any, Self

from fortytwo.resources.project_user.project_user import ProjectUser
from fortytwo.resources.resource import Resource, ResourceTemplate


class GetProjectUsers(Resource[list[ProjectUser]]):
    """
    Resource for fetching all project users.

    Returns a list of project user records showing student progress
    on projects.
    Supports pagination via parameters.
    """

    method: str = "GET"
    _url: str = "/projects_users"

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [ProjectUser(project_user) for project_user in response_data]


class GetProjectUsersByProject(Resource[list[ProjectUser]]):
    """
    Resource for fetching project users for a specific project.

    Returns a list of project user records for students working on
    the specified project.

    Args:
        project_id: The ID of the project to fetch project users for.
    """

    method: str = "GET"
    _url: str = "/projects/%s/projects_users"

    def __init__(self: Self, project_id: int) -> None:
        self.project_id = project_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.project_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [ProjectUser(project_user) for project_user in response_data]


class GetProjectUserById(Resource[ProjectUser]):
    """
    Resource for fetching a specific project user by ID.

    Args:
        project_user_id: The ID of the project user to fetch.
    """

    method: str = "GET"
    _url: str = "/projects_users/%s"

    def __init__(self: Self, project_user_id: int) -> None:
        self.project_user_id = project_user_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.project_user_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return ProjectUser(response_data)


class GetProjectUsersByUserId(Resource[list[ProjectUser]]):
    """
    Resource for fetching project users for a specific user.

    Returns a list of project user records for projects the specified
    user has worked on.

    Args:
        user_id: The ID of the user to fetch project users for.
    """

    method: str = "GET"
    _url: str = "/users/%s/projects_users"

    def __init__(self: Self, user_id: int) -> None:
        self.user_id = user_id

    @property
    def url(self: Self) -> str:
        return self.config.request_endpoint + self._url % self.user_id

    def parse_response(self: Self, response_data: Any) -> ResourceTemplate:
        return [ProjectUser(project_user) for project_user in response_data]

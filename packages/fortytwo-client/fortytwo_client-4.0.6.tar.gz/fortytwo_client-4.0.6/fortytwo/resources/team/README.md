# Team Resource

The Team resource provides access to team data from the 42 API.

## Overview

This module allows you to fetch team information from the 42 API, including team members, project assignments, validation status, and repository details. Teams represent groups of students working together on projects.

## Classes

### `TeamUser`
Represents a user within a team context.

**Properties:**
- `id` (int): User's ID
- `login` (str): User's login name
- `url` (str): API URL for the user
- `leader` (bool): Whether this user is the team leader
- `occurrence` (int): Occurrence number for this project attempt
- `validated` (bool): Whether the user's participation is validated
- `projects_user_id` (int): Associated project user ID

### `Team`
Represents a team working on a project.

**Properties:**
- `id` (int): Team's unique identifier
- `name` (str): Team name
- `url` (str): API URL for the team
- `final_mark` (int | None): Final grade received (None if not graded)
- `project_id` (int): ID of the project this team is working on
- `created_at` (datetime): When the team was created
- `updated_at` (datetime): When the team was last updated
- `status` (str): Current status of the team (e.g., "waiting_for_correction", "in_progress")
- `terminating_at` (datetime | None): When the team will terminate
- `users` (list[TeamUser]): List of team members
- `locked` (bool): Whether the team is locked
- `validated` (bool | None): Whether the team's work is validated (None if pending)
- `closed` (bool): Whether the team is closed
- `repo_url` (str | None): Git repository URL
- `repo_uuid` (str): Unique identifier for the repository
- `locked_at` (datetime | None): When the team was locked
- `closed_at` (datetime | None): When the team was closed
- `project_session_id` (int): Associated project session ID

### Resource Classes

#### `GetTeams`
Fetches all teams with optional filtering.
- **Endpoint:** `/teams`
- **Method:** GET
- **Returns:** `List[Team]`

#### `GetTeamsByCursusId`
Fetches all teams for a specific cursus.
- **Endpoint:** `/cursus/{cursus_id}/teams`
- **Method:** GET
- **Returns:** `List[Team]`

#### `GetTeamsByUserId`
Fetches all teams for a specific user.
- **Endpoint:** `/users/{user_id}/teams`
- **Method:** GET
- **Returns:** `List[Team]`

#### `GetTeamsByProjectId`
Fetches all teams for a specific project.
- **Endpoint:** `/projects/{project_id}/teams`
- **Method:** GET
- **Returns:** `List[Team]`

#### `GetTeamsByUserIdAndProjectId`
Fetches all teams for a specific user and project combination.
- **Endpoint:** `/users/{user_id}/projects/{project_id}/teams`
- **Method:** GET
- **Returns:** `List[Team]`

## Usage Examples

### Using the Manager (Recommended)

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException

client = Client(
    ...
)

# Get teams for a specific user
try:
    user = client.users.get_by_login("jdoe")
    teams = client.teams.get_by_user_id(user.id)
    for team in teams:
        print(f"Team: {team.name}")
        print(f"  Status: {team.status}")
        print(f"  Final Mark: {team.final_mark}")
except FortyTwoNotFoundException:
    print("User not found")

# Get teams for a specific project
teams = client.teams.get_by_project_id(project_id=1314, page=1, page_size=50)
for team in teams:
    print(f"{team.id}: {team.name} - {team.status}")

# Get teams for a specific cursus
teams = client.teams.get_by_cursus_id(cursus_id=21)
for team in teams:
    leader = next((u for u in team.users if u.leader), None)
    if leader:
        print(f"{team.name} - Leader: {leader.login}")

# Get all teams with pagination
teams = client.teams.get_all(page=1, page_size=100)
```

### Using Resources Directly

```python
from fortytwo.resources.team.resource import (
    GetTeams,
    GetTeamsByUserId,
    GetTeamsByProjectId
)

# Get all teams
teams = client.request(GetTeams())

# Get teams for a specific user
teams = client.request(GetTeamsByUserId(12345))

# Get teams for a specific project
teams = client.request(GetTeamsByProjectId(1314))
```

## Data Structure

### Team JSON Response
```json
{
  "id": 5253824,
  "name": "jdoe's group",
  "url": "https://api.intra.42.fr/v2/teams/5253824",
  "final_mark": 125,
  "project_id": 1314,
  "created_at": "2023-11-15T10:30:00.000Z",
  "updated_at": "2023-11-20T14:15:00.000Z",
  "status": "finished",
  "terminating_at": null,
  "users": [
    {
      "id": 123456,
      "login": "jdoe",
      "url": "https://api.intra.42.fr/v2/users/jdoe",
      "leader": true,
      "occurrence": 0,
      "validated": true,
      "projects_user_id": 3456789
    },
    {
      "id": 123457,
      "login": "asmith",
      "url": "https://api.intra.42.fr/v2/users/asmith",
      "leader": false,
      "occurrence": 0,
      "validated": true,
      "projects_user_id": 3456790
    }
  ],
  "locked?": true,
  "validated?": true,
  "closed?": true,
  "repo_url": "git@vogsphere.42.fr:vogsphere/intra-uuid-abc-123",
  "repo_uuid": "intra-uuid-abc-123",
  "locked_at": "2023-11-18T09:00:00.000Z",
  "closed_at": "2023-11-20T14:15:00.000Z",
  "project_session_id": 5678
}
```

## Parameters

For detailed information about filtering, sorting, ranging, and custom parameters for team queries, see the [Team Parameters Documentation](parameter/README.md).

## Error Handling

All methods raise exceptions on errors:

```python
from fortytwo import Client
from fortytwo.exceptions import (
    FortyTwoNotFoundException,
    FortyTwoUnauthorizedException,
    FortyTwoRateLimitException,
    FortyTwoNetworkException,
    FortyTwoRequestException
)

client = Client(
    ...
)

try:
    teams = client.teams.get_by_user_id(user_id=99999)
    print(f"Found {len(teams)} teams")
except FortyTwoNotFoundException:
    print("User not found")
except FortyTwoUnauthorizedException:
    print("Authentication failed")
except FortyTwoRateLimitException as e:
    print(f"Rate limit exceeded. Wait {e.wait_time} seconds")
except FortyTwoNetworkException:
    print("Network error occurred")
except FortyTwoRequestException as e:
    print(f"Request failed: {e}")
```

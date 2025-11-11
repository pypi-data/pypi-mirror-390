# Project User Resource

The Project User resource provides access to project completion data, tracking user progress, grades, and team information for 42 School projects.

## Overview

This module allows you to fetch project completion information from the 42 API, including grades, status, team details, and project progression data.

## Classes

### `ProjectUser`
Represents a user's completion record for a specific project.

**Properties:**
- `id` (int): Project user ID
- `occurrence` (int): Occurrence number
- `final_mark` (Optional[int]): Final grade received (0-100+), None if not yet graded
- `status` (str): Completion status ("finished", "in_progress", "waiting_for_correction", etc.)
- `validated` (Optional[bool]): Whether the project was validated, None if not yet determined
- `current_team_id` (int): Current team ID
- `project` (ProjectReference): The project being completed (contains id, name, slug, parent_id)
- `user` (User): The user working on the project
- `cursus_ids` (List[int]): List of cursus IDs this project user belongs to
- `marked_at` (Optional[datetime]): When the project was marked/corrected, None if not yet marked
- `marked` (bool): Whether the project has been marked
- `retriable_at` (Optional[datetime]): When the project can be retried, None if not applicable
- `created_at` (datetime): When the project was started
- `updated_at` (datetime): Last update to the project status

### Resource Classes

#### `GetProjectUserById`
Fetches a specific project user by ID.
- **Endpoint:** `/projects_users/{id}`
- **Method:** GET
- **Returns:** `ProjectUser`

#### `GetProjectUsers`
Fetches project completion records with filtering options.
- **Endpoint:** `/projects_users`
- **Method:** GET
- **Returns:** `List[ProjectUser]`

#### `GetProjectUsersByProject`
Fetches all completions for a specific project.
- **Endpoint:** `/projects/{project_id}/projects_users`
- **Method:** GET
- **Returns:** `List[ProjectUser]`

#### `GetProjectUsersByUserId`
Fetches all project completions for a specific user.
- **Endpoint:** `/users/{user_id}/projects_users`
- **Method:** GET
- **Returns:** `List[ProjectUser]`

## Usage Examples

### Using the Manager (Recommended)

```python
from fortytwo import Client

client = Client(
    ...
)

# Get a specific project user by ID
try:
    project_user = client.project_users.get_by_id(project_user_id=3899604)
    print(f"User: {project_user.user.login}")
    print(f"Project: {project_user.project.name}")
    print(f"Status: {project_user.status}")
    if project_user.final_mark is not None:
        print(f"Grade: {project_user.final_mark}/100")
        if project_user.validated:
            print("✅ Validated!")
    else:
        print("Not yet graded")
except FortyTwoNotFoundException:
    print("Project user not found")

# Get all project completions with pagination
all_project_users = client.project_users.get_all(page=1, page_size=100)
print(f"Found {len(all_project_users)} project completions")

# Show grades
for pu in all_project_users:
    status_emoji = "✅" if pu.status == "finished" else "🔄"
    grade = f"{pu.final_mark}/100" if pu.final_mark is not None else "Not graded"
    print(f"{status_emoji} {pu.user.login} - {pu.project.name}: {grade}")

# Get all completions for a specific project with pagination
project_completions = client.project_users.get_by_project_id(
    project_id=1,
    page=1,
    page_size=50
)
if project_completions:
    graded = [p for p in project_completions if p.final_mark is not None]
    if graded:
        avg_grade = sum(p.final_mark for p in graded) / len(graded)
        print(f"Average grade for this project: {avg_grade:.1f}/100")

# Get all project completions for a specific user with pagination
user_projects = client.project_users.get_by_user_id(
    user_id=132246,
    page=1,
    page_size=50
)
print(f"User has {len(user_projects)} project attempts")
for pu in user_projects:
    grade = f"{pu.final_mark}/100" if pu.final_mark is not None else "Not graded"
    print(f"  - {pu.project.name}: {grade} ({pu.status})")
```

### Using Resources Directly

```python
from fortytwo.resources.project_user.resource import (
    GetProjectUserById,
    GetProjectUsers,
    GetProjectUsersByProject,
    GetProjectUsersByUserId,
)

# Get a specific project user
project_user = client.request(GetProjectUserById(12345))

# Get all project users
all_completions = client.request(GetProjectUsers())

# Get completions for a specific project
project_completions = client.request(GetProjectUsersByProject(1))

# Get completions for a specific user
user_completions = client.request(GetProjectUsersByUserId(12345))
```
user_completions = client.request(GetProjectUsersByUserId(12345))

# Get project completion statistics
project_stats = client.request(GetProjectUsersByProjectId(1))
```

## Data Structure

### Project User JSON Response
```json
{
  "id": 456789,
  "name": "team_name",
  "status": "finished",
  "final_mark": 95,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-22T16:30:00Z"
}
```

## Parameters

For detailed information about filtering and ranging project_user queries, see the [ProjectUser Parameters Documentation](parameter/README.md).

> [!NOTE]
> Note: ProjectUser resources do not support sorting parameters.

## Error Handling

Methods raise exceptions on errors:

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoRequestException

client = Client(
    ...
)

try:
    projects = client.project_users.get_all(page=1, page_size=100)
    if not projects:
        print("No project completions found")
    else:
        print(f"Found {len(projects)} project completions")
except FortyTwoRequestException as e:
    print(f"Request failed: {e}")
```

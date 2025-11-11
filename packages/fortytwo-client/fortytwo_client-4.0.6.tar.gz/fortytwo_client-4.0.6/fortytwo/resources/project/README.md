# Project Resource

The Project resource provides access to 42 School project data and curriculum information.

## Overview

This module allows you to fetch project information from the 42 API, including project details, difficulty levels, relationships, and curriculum structure.

## Classes

### `ProjectReference`
Lightweight representation of a project reference used in parent/children relationships.

**Properties:**
- `id` (int): Project identifier
- `name` (str): Project name
- `slug` (str): URL-friendly project identifier

### `Project`
Represents a 42 School project with all associated metadata.

**Properties:**
- `id` (int): Unique project identifier
- `name` (str): Project name
- `slug` (str): URL-friendly project identifier
- `difficulty` (int): Project difficulty level
- `exam` (bool): Whether this project is an exam
- `parent` (Optional[ProjectReference]): Parent project in curriculum tree
- `children` (List[ProjectReference]): Child projects in curriculum tree
- `created_at` (datetime): Project creation date
- `updated_at` (datetime): Last project update date
- `cursus` (List[Cursus]): List of cursus this project belongs to
- `campus` (List[Campus]): List of campuses where this project is available

### Resource Classes

#### `GetProjectsById`
Fetches a single project by its ID.
- **Endpoint:** `/projects/{id}`
- **Method:** GET
- **Returns:** `Project`

#### `GetProjects`
Fetches all projects with optional filtering.
- **Endpoint:** `/projects`
- **Method:** GET
- **Returns:** `List[Project]`

#### `GetProjectsByCursusId`
Fetches projects for a specific cursus.
- **Endpoint:** `/cursus/{cursus_id}/projects`
- **Method:** GET
- **Returns:** `List[Project]`

#### `GetProjectsByProjectId`
Fetches all sub-projects for a specific parent project.
- **Endpoint:** `/projects/{project_id}/projects`
- **Method:** GET
- **Returns:** `List[Project]`

## Usage Examples

### Using the Manager (Recommended)

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException

client = Client(
    ...
)

# Get a specific project
try:
    project = client.projects.get_by_id(project_id=1)
    print(f"Project: {project.name}")
    print(f"Difficulty: {project.difficulty}/5")
    print(f"Is Exam: {project.exam}")

    # Access parent project if it exists
    if project.parent:
        print(f"Parent: {project.parent.name} (ID: {project.parent.id})")

    # Access child projects
    if project.children:
        print(f"Child projects: {len(project.children)}")
        for child in project.children:
            print(f"  - {child.name} (ID: {child.id})")

except FortyTwoNotFoundException:
    print("Project not found")

# Get all projects with pagination
projects = client.projects.get_all(page=1, page_size=50)

# Get projects by cursus ID with pagination
cursus_projects = client.projects.get_by_cursus_id(cursus_id=21, page=1, page_size=25)

# Get sub-projects of a specific project
sub_projects = client.projects.get_by_project_id(project_id=1, page=1, page_size=25)
for sub_project in sub_projects:
    print(f"  - {sub_project.name} (Difficulty: {sub_project.difficulty})")
```

### Using Resources Directly

```python
from fortytwo.resources.project.resource import (
    GetProjectsById,
    GetProjects,
    GetProjectsByCursusId,
    GetProjectsByProjectId
)

# Get a specific project
project = client.request(GetProjectsById(1))

# Get all projects
projects = client.request(GetProjects())

# Get projects by cursus
cursus_projects = client.request(GetProjectsByCursusId(21))

# Get sub-projects
sub_projects = client.request(GetProjectsByProjectId(1))
```

## Data Structure

### Project JSON Response
```json
{
  "id": 1,
  "name": "Libft",
  "slug": "libft",
  "difficulty": 5000,
  "parent": null,
  "children": [],
  "created_at": "2017-11-22T13:41:25.963Z",
  "updated_at": "2017-11-22T13:41:26.243Z",
  "exam": false,
  "cursus": [
    {
      "id": 1,
      "created_at": "2017-11-22T13:41:00.750Z",
      "name": "Piscine C",
      "slug": "piscine-c",
      "kind": "piscine"
    }
  ],
  "campus": [
    {
      "id": 1,
      "name": "Cluj",
      "time_zone": "Europe/Bucharest",
      "language": {
        "id": 3,
        "name": "Romanian",
        "identifier": "ro",
        "created_at": "2017-11-22T13:40:59.468Z",
        "updated_at": "2017-11-22T13:41:26.139Z"
      },
      "users_count": 28,
      "vogsphere_id": 1
    }
  ]
}
```

## Parameters

For detailed information about filtering, sorting, and ranging project queries, see the [Project Parameters Documentation](parameter/README.md).

## Error Handling

All methods raise exceptions on errors:

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException, FortyTwoRequestException

client = Client(
    ...
)

try:
    project = client.projects.get_by_id(project_id=99999)
    print(f"Found project: {project.name}")
except FortyTwoNotFoundException:
    print("Project not found")
except FortyTwoRequestException as e:
    print(f"Request failed: {e}")
```

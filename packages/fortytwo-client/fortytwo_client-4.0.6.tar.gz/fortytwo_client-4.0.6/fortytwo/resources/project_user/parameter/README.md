# Project User Parameters

This document describes all available parameters for filtering, sorting, and ranging ProjectUser resources in the 42 API.

## Overview

ProjectUser parameters allow you to customize queries to the 42 API's projects_users endpoint. You can:
- **Filter** - Find project-user associations matching specific criteria
- **Range** - Retrieve project-users within a specific range of values

> [!NOTE]
> Note: ProjectUser resources do not support sorting parameters.

## Usage

```python
from fortytwo import Client, parameter

client = Client(
    ...
)

# Using project_user-specific parameters
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_user_id(12345),
    parameter.ProjectUserParameters.Filter.by_status("finished"),
    parameter.PageSize(100)
)
```

## Filter Parameters

Filters narrow down results to match specific criteria.

### `by_id(project_user_id)`
Filter project-user associations by their unique ID.

**Parameters:**
- `project_user_id` (str | int): The project_user ID to filter by

**Example:**
```python
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_id(123456)
)
```

---

### `by_project_id(project_id)`
Filter by project ID.

**Parameters:**
- `project_id` (str | int): The project ID to filter by

**Example:**
```python
# Get all users working on ft_transcendence
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_project_id(1337)
)
```

---

### `by_user_id(user_id)`
Filter by user ID.

**Parameters:**
- `user_id` (str | int): The user ID to filter by

**Example:**
```python
# Get all projects for a specific user
user_projects = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_user_id(12345)
)
```

---

### `by_created_at(created_at)`
Filter by creation date.

**Parameters:**
- `created_at` (str | datetime): The creation date (ISO format string or datetime object)

**Example:**
```python
from datetime import datetime

project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_created_at("2024-01-01T00:00:00Z")
)
```

---

### `by_updated_at(updated_at)`
Filter by last update date.

**Parameters:**
- `updated_at` (str | datetime): The update date (ISO format string or datetime object)

**Example:**
```python
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_updated_at("2024-10-01T00:00:00Z")
)
```

---

### `by_occurrence(occurrence)`
Filter by project occurrence number (for retries).

**Parameters:**
- `occurrence` (str | int): The occurrence number

**Example:**
```python
# Get first attempts only
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_occurrence(0)
)

# Get second attempts
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_occurrence(1)
)
```

---

### `by_final_mark(final_mark)`
Filter by exact final mark/score.

**Parameters:**
- `final_mark` (str | int): The final mark to filter by

**Example:**
```python
# Get perfect scores
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_final_mark(100)
)
```

---

### `by_retriable_at(retriable_at)`
Filter by when the project becomes retriable.

**Parameters:**
- `retriable_at` (str | datetime): The retriable date (ISO format string or datetime object)

**Example:**
```python
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_retriable_at("2024-12-01T00:00:00Z")
)
```

---

### `by_marked_at(marked_at)`
Filter by when the project was marked/graded.

**Parameters:**
- `marked_at` (str | datetime): The marked date (ISO format string or datetime object)

**Example:**
```python
from datetime import datetime

today = datetime.now()
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_marked_at(today)
)
```

---

### `by_status(status)`
Filter by project status.

**Parameters:**
- `status` (str): Status value (e.g., "finished", "in_progress", "waiting_for_correction", "searching_a_group")

**Common Status Values:**
- `"finished"` - Project completed and validated
- `"in_progress"` - Currently working on the project
- `"waiting_for_correction"` - Submitted, awaiting evaluation
- `"searching_a_group"` - Looking for team members
- `"creating_group"` - Forming a team

**Example:**
```python
# Get all finished projects for a user
finished_projects = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_user_id(12345),
    parameter.ProjectUserParameters.Filter.by_status("finished")
)

# Get projects currently in progress
in_progress = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_status("in_progress")
)
```

---

### `by_cursus(cursus)`
Filter by cursus ID.

**Parameters:**
- `cursus` (str | int): The cursus ID

**Example:**
```python
# Get project-users in the 42 cursus (ID: 21)
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_cursus(21)
)
```

---

### `by_campus(campus)`
Filter by campus ID.

**Parameters:**
- `campus` (str | int): The campus ID

**Example:**
```python
# Get project-users at Paris campus (ID: 1)
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_campus(1)
)
```

---

### `retriable_only()`
Filter to show only retriable projects (failed projects that can be retried).

**Example:**
```python
# Get all retriable projects for a user
retriable = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_user_id(12345),
    parameter.ProjectUserParameters.Filter.retriable_only()
)
```

---

### `non_retriable_only()`
Filter to show only non-retriable projects.

**Example:**
```python
non_retriable = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.non_retriable_only()
)
```

---

### `marked_only()`
Filter to show only marked/graded projects.

**Example:**
```python
# Get all marked projects for a user
marked = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_user_id(12345),
    parameter.ProjectUserParameters.Filter.marked_only()
)
```

---

### `non_marked_only()`
Filter to show only non-marked projects (not yet graded).

**Example:**
```python
# Get projects awaiting evaluation
awaiting_eval = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.non_marked_only()
)
```

---

## Range Parameters

Range parameters retrieve project-users with values between a minimum and maximum.

All range methods accept optional `min` and `max` parameters. You can specify one or both.

### `id_range(min_id=None, max_id=None)`
Filter project-users with IDs in a specific range.

**Parameters:**
- `min_id` (str | int, optional): Minimum ID (inclusive)
- `max_id` (str | int, optional): Maximum ID (inclusive)

**Example:**
```python
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.id_range(1000, 2000)
)
```

---

### `project_id_range(min_project_id=None, max_project_id=None)`
Filter by project ID range.

**Parameters:**
- `min_project_id` (str | int, optional): Minimum project ID (inclusive)
- `max_project_id` (str | int, optional): Maximum project ID (inclusive)

**Example:**
```python
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.project_id_range(100, 200)
)
```

---

### `user_id_range(min_user_id=None, max_user_id=None)`
Filter by user ID range.

**Parameters:**
- `min_user_id` (str | int, optional): Minimum user ID (inclusive)
- `max_user_id` (str | int, optional): Maximum user ID (inclusive)

**Example:**
```python
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.user_id_range(10000, 20000)
)
```

---

### `created_at_range(start_date=None, end_date=None)`
Filter by creation date range.

**Parameters:**
- `start_date` (str | datetime, optional): Start date (inclusive)
- `end_date` (str | datetime, optional): End date (inclusive)

**Example:**
```python
from datetime import datetime

# Projects started in 2024
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.created_at_range(
        datetime(2024, 1, 1),
        datetime(2024, 12, 31)
    )
)
```

---

### `updated_at_range(start_date=None, end_date=None)`
Filter by update date range.

**Parameters:**
- `start_date` (str | datetime, optional): Start date (inclusive)
- `end_date` (str | datetime, optional): End date (inclusive)

**Example:**
```python
from datetime import datetime, timedelta

# Projects updated in the last 7 days
start = datetime.now() - timedelta(days=7)
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.updated_at_range(start_date=start)
)
```

---

### `occurrence_range(min_occurrence=None, max_occurrence=None)`
Filter by occurrence range (retry attempts).

**Parameters:**
- `min_occurrence` (str | int, optional): Minimum occurrence (inclusive)
- `max_occurrence` (str | int, optional): Maximum occurrence (inclusive)

**Example:**
```python
# First or second attempts only
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.occurrence_range(0, 1)
)
```

---

### `final_mark_range(min_final_mark=None, max_final_mark=None)`
Filter by final mark range.

**Parameters:**
- `min_final_mark` (str | int, optional): Minimum mark (inclusive)
- `max_final_mark` (str | int, optional): Maximum mark (inclusive)

**Example:**
```python
# Passing grades (80+)
passing = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.final_mark_range(min_final_mark=80)
)

# Excellent scores (95-100)
excellent = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.final_mark_range(95, 100)
)

# Failed projects (0-79)
failed = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.final_mark_range(0, 79)
)
```

---

### `retriable_at_range(start_date=None, end_date=None)`
Filter by retriable date range.

**Parameters:**
- `start_date` (str | datetime, optional): Start date (inclusive)
- `end_date` (str | datetime, optional): End date (inclusive)

**Example:**
```python
from datetime import datetime, timedelta

# Projects that become retriable in the next 7 days
start = datetime.now()
end = start + timedelta(days=7)

project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.retriable_at_range(start, end)
)
```

---

### `marked_at_range(start_date=None, end_date=None)`
Filter by marked date range.

**Parameters:**
- `start_date` (str | datetime, optional): Start date (inclusive)
- `end_date` (str | datetime, optional): End date (inclusive)

**Example:**
```python
from datetime import datetime, timedelta

# Projects marked in the last 24 hours
start = datetime.now() - timedelta(hours=24)

recently_marked = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.marked_at_range(start_date=start)
)
```

---

### `status_range(min_status=None, max_status=None)`
Filter by status range (alphabetical).

**Parameters:**
- `min_status` (str, optional): Minimum status (inclusive)
- `max_status` (str, optional): Maximum status (inclusive)

**Example:**
```python
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Range.status_range("finished", "waiting_for_correction")
)
```

---

## Combining Parameters

You can combine multiple parameters to create complex queries:

```python
# Get all finished projects with excellent scores for a user
excellent_projects = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_user_id(12345),
    parameter.ProjectUserParameters.Filter.by_status("finished"),
    parameter.ProjectUserParameters.Range.final_mark_range(95, 100),
    parameter.PageSize(50)
)

# Get all first attempts in progress
first_attempts = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_occurrence(0),
    parameter.ProjectUserParameters.Filter.by_status("in_progress")
)

# Get all marked projects in a cursus from the last month
from datetime import datetime, timedelta

one_month_ago = datetime.now() - timedelta(days=30)
recent_marked = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_cursus(21),
    parameter.ProjectUserParameters.Filter.marked_only(),
    parameter.ProjectUserParameters.Range.marked_at_range(start_date=one_month_ago),
    parameter.PageSize(100)
)
```

## Common Use Cases

### Get all projects for a user
```python
user_projects = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_user_id(12345)
)
```

### Get completed projects for a user
```python
completed = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_user_id(12345),
    parameter.ProjectUserParameters.Filter.by_status("finished")
)
```

### Get projects awaiting evaluation
```python
awaiting_eval = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_user_id(12345),
    parameter.ProjectUserParameters.Filter.by_status("waiting_for_correction")
)
```

### Get all users who worked on a project
```python
project_participants = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_project_id(1337)
)
```

### Get failed projects available for retry
```python
retriable = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_user_id(12345),
    parameter.ProjectUserParameters.Filter.retriable_only()
)
```

### Calculate average score for a project
```python
project_users = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_project_id(1337),
    parameter.ProjectUserParameters.Filter.marked_only()
)

if project_users:
    total = sum(pu.final_mark for pu in project_users if pu.final_mark is not None)
    avg = total / len(project_users)
    print(f"Average score: {avg:.2f}")
```

### Find high performers in a cursus
```python
high_performers = client.project_users.get_all(
    parameter.ProjectUserParameters.Filter.by_cursus(21),
    parameter.ProjectUserParameters.Filter.by_status("finished"),
    parameter.ProjectUserParameters.Range.final_mark_range(min_final_mark=100),
    parameter.PageSize(100)
)
```

## Examples

See the [`example/`](../../../../example/) directory for complete working examples.

# Team Parameters

This module provides filtering, sorting, ranging, and custom parameters for team queries.

## Overview

The Team Parameters module allows you to:
- **Filter** teams by specific field values
- **Sort** teams by any field in ascending or descending order
- **Range** teams by numeric or date field boundaries
- **Custom Parameters** for additional filtering options (cursus_id, user_id, project_id, project_session_id)

## Usage

```python
from fortytwo import Client
from fortytwo.resources.team import TeamParameters
from fortytwo.request.parameter.parameter import SortDirection

client = Client(
    ...
)

# Filter by status
teams = client.teams.get_all(
    TeamParameters.Filter.by_status("finished")
)

# Sort by creation date
teams = client.teams.get_all(
    TeamParameters.Sort.by_created_at(SortDirection.DESCENDING)
)

# Range by final mark
teams = client.teams.get_all(
    TeamParameters.Range.by_final_mark(min_final_mark=80, max_final_mark=125)
)

# Use custom parameters
teams = client.teams.get_all(
    TeamParameters.Parameter.cursus_id(21),
    TeamParameters.Parameter.project_id(1314)
)

# Combine multiple parameters
teams = client.teams.get_all(
    TeamParameters.Filter.by_validated(True),
    TeamParameters.Sort.by_final_mark(SortDirection.DESCENDING),
    TeamParameters.Parameter.cursus_id(21)
)
```

---

## Custom Parameters

Custom parameters for team-specific filtering.

### `Parameter.cursus_id(cursus_id: Union[str, int])`
The cursus id or slug.

**Args:**
- `cursus_id` (Union[str, int]): The cursus id or slug

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Parameter.cursus_id(21)
)
```

### `Parameter.user_id(user_id: Union[str, int])`
The user id or slug.

**Args:**
- `user_id` (Union[str, int]): The user id or slug

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Parameter.user_id("jdoe")
)
```

### `Parameter.project_id(project_id: Union[str, int])`
The project id or slug.

**Args:**
- `project_id` (Union[str, int]): The project id or slug

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Parameter.project_id(1314)
)
```

### `Parameter.project_session_id(project_session_id: Union[str, int])`
The project session id.

**Args:**
- `project_session_id` (Union[str, int]): The project session id

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Parameter.project_session_id(5678)
)
```

---

## Filter Parameters

Filter teams by specific field values.

### `by_id(team_id: Union[str, int])`
Filter by team ID.

**Args:**
- `team_id` (Union[str, int]): The team ID

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_id(5253824)
)
```

### `by_project_id(project_id: Union[str, int])`
Filter by project ID.

**Args:**
- `project_id` (Union[str, int]): The project ID

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_project_id(1314)
)
```

### `by_name(name: str)`
Filter by team name.

**Args:**
- `name` (str): The team name

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_name("jdoe's group")
)
```

### `by_created_at(created_at: Union[str, datetime])`
Filter by team creation date.

**Args:**
- `created_at` (Union[str, datetime]): The creation date (ISO 8601 format string or datetime object)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_created_at("2023-11-15T10:30:00.000Z")
)
```

### `by_updated_at(updated_at: Union[str, datetime])`
Filter by team last update date.

**Args:**
- `updated_at` (Union[str, datetime]): The update date (ISO 8601 format string or datetime object)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_updated_at("2023-11-20T14:15:00.000Z")
)
```

### `by_locked_at(locked_at: Union[str, datetime])`
Filter by team lock date.

**Args:**
- `locked_at` (Union[str, datetime]): The lock date (ISO 8601 format string or datetime object)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_locked_at("2023-11-18T09:00:00.000Z")
)
```

### `by_closed_at(closed_at: Union[str, datetime])`
Filter by team close date.

**Args:**
- `closed_at` (Union[str, datetime]): The close date (ISO 8601 format string or datetime object)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_closed_at("2023-11-20T14:15:00.000Z")
)
```

### `by_final_mark(final_mark: Union[str, int])`
Filter by team final mark.

**Args:**
- `final_mark` (Union[str, int]): The final mark

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_final_mark(125)
)
```

### `by_repo_url(repo_url: str)`
Filter by repository URL.

**Args:**
- `repo_url` (str): The repository URL

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_repo_url("git@vogsphere.42.fr:vogsphere/intra-uuid-abc-123")
)
```

### `by_repo_uuid(repo_uuid: str)`
Filter by repository UUID.

**Args:**
- `repo_uuid` (str): The repository UUID

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_repo_uuid("intra-uuid-abc-123")
)
```

### `by_deadline_at(deadline_at: Union[str, datetime])`
Filter by team deadline date.

**Args:**
- `deadline_at` (Union[str, datetime]): The deadline date (ISO 8601 format string or datetime object)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_deadline_at("2023-12-01T23:59:59.000Z")
)
```

### `by_terminating_at(terminating_at: Union[str, datetime])`
Filter by team terminating date.

**Args:**
- `terminating_at` (Union[str, datetime]): The terminating date (ISO 8601 format string or datetime object)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_terminating_at("2023-12-15T23:59:59.000Z")
)
```

### `by_project_session_id(project_session_id: Union[str, int])`
Filter by project session ID.

**Args:**
- `project_session_id` (Union[str, int]): The project session ID

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_project_session_id(5678)
)
```

### `by_status(status: str)`
Filter by team status.

**Args:**
- `status` (str): The team status (e.g., "waiting_for_correction", "in_progress", "finished")

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_status("finished")
)
```

### `by_cursus(cursus: Union[str, bool])`
Filter by cursus.

**Args:**
- `cursus` (Union[str, bool]): The cursus to filter by

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_cursus("21")
)
```

### `by_active_cursus(active_cursus: Union[str, bool])`
Filter by active cursus.

**Args:**
- `active_cursus` (Union[str, bool]): The active cursus to filter by

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_active_cursus(True)
)
```

### `by_campus(campus: Union[str, bool])`
Filter by campus.

**Args:**
- `campus` (Union[str, bool]): The campus to filter by

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_campus("paris")
)
```

### `by_primary_campus(primary_campus: Union[str, bool])`
Filter by primary campus.

**Args:**
- `primary_campus` (Union[str, bool]): The primary campus to filter by

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_primary_campus(True)
)
```

### `by_locked(locked: Union[str, bool])`
Filter by locked status.

**Args:**
- `locked` (Union[str, bool]): The locked status

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_locked(True)
)
```

### `by_closed(closed: Union[str, bool])`
Filter by closed status.

**Args:**
- `closed` (Union[str, bool]): The closed status

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_closed(False)
)
```

### `by_deadline(deadline: Union[str, bool])`
Filter by deadline.

**Args:**
- `deadline` (Union[str, bool]): The deadline to filter by

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_deadline(True)
)
```

### `by_terminating(terminating: Union[str, bool])`
Filter by terminating status.

**Args:**
- `terminating` (Union[str, bool]): The terminating status

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_terminating(False)
)
```

### `by_with_mark(with_mark: Union[str, bool])`
Filter by with_mark status.

**Args:**
- `with_mark` (Union[str, bool]): The with_mark status

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Filter.by_with_mark(True)
)
```

---

## Sort Parameters

Sort teams by specific fields in ascending or descending order.

> **Note**: All sort methods use the `SortDirection` enum to specify ascending or descending order. Import it with:
> ```python
> from fortytwo.request.parameter.parameter import SortDirection
> ```

### `by_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by team ID.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_id(SortDirection.ASCENDING)
)
```

### `by_project_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by project ID.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_project_id(SortDirection.ASCENDING)
)
```

### `by_name(direction: SortDirection = SortDirection.ASCENDING)`
Sort by team name.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_name(SortDirection.ASCENDING)
)
```

### `by_created_at(direction: SortDirection = SortDirection.ASCENDING)`
Sort by creation date.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_created_at(SortDirection.DESCENDING)
)
```

### `by_updated_at(direction: SortDirection = SortDirection.ASCENDING)`
Sort by update date.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_updated_at(SortDirection.DESCENDING)
)
```

### `by_locked_at(direction: SortDirection = SortDirection.ASCENDING)`
Sort by lock date.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_locked_at(SortDirection.DESCENDING)
)
```

### `by_closed_at(direction: SortDirection = SortDirection.ASCENDING)`
Sort by close date.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_closed_at(SortDirection.DESCENDING)
)
```

### `by_final_mark(direction: SortDirection = SortDirection.ASCENDING)`
Sort by final mark.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_final_mark(SortDirection.DESCENDING)
)
```

### `by_repo_url(direction: SortDirection = SortDirection.ASCENDING)`
Sort by repository URL.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_repo_url(SortDirection.ASCENDING)
)
```

### `by_repo_uuid(direction: SortDirection = SortDirection.ASCENDING)`
Sort by repository UUID.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_repo_uuid(SortDirection.ASCENDING)
)
```

### `by_deadline_at(direction: SortDirection = SortDirection.ASCENDING)`
Sort by deadline date.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_deadline_at(SortDirection.ASCENDING)
)
```

### `by_terminating_at(direction: SortDirection = SortDirection.ASCENDING)`
Sort by terminating date.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_terminating_at(SortDirection.ASCENDING)
)
```

### `by_project_session_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by project session ID.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_project_session_id(SortDirection.ASCENDING)
)
```

### `by_status(direction: SortDirection = SortDirection.ASCENDING)`
Sort by status.

**Args:**
- `direction` (SortDirection): Sort direction. Default is `SortDirection.ASCENDING`.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

teams = client.teams.get_all(
    TeamParameters.Sort.by_status(SortDirection.ASCENDING)
)
```

---

## Range Parameters

Filter teams by numeric or date field boundaries.

### `by_id(min_id: Union[str, int], max_id: Union[str, int])`
Filter by team ID range.

**Args:**
- `min_id` (Union[str, int]): The minimum ID value (inclusive)
- `max_id` (Union[str, int]): The maximum ID value (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_id(min_id=1000000, max_id=2000000)
)
```

### `by_project_id(min_project_id: Union[str, int], max_project_id: Union[str, int])`
Filter by project ID range.

**Args:**
- `min_project_id` (Union[str, int]): The minimum project ID value (inclusive)
- `max_project_id` (Union[str, int]): The maximum project ID value (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_project_id(min_project_id=1000, max_project_id=2000)
)
```

### `by_name(min_name: str, max_name: str)`
Filter by team name range.

**Args:**
- `min_name` (str): The minimum name value (inclusive)
- `max_name` (str): The maximum name value (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_name(min_name="a", max_name="m")
)
```

### `by_created_at(min_created_at: Union[str, datetime], max_created_at: Union[str, datetime])`
Filter by creation date range.

**Args:**
- `min_created_at` (Union[str, datetime]): The minimum creation date (inclusive)
- `max_created_at` (Union[str, datetime]): The maximum creation date (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_created_at(
        min_created_at="2023-01-01T00:00:00.000Z",
        max_created_at="2023-12-31T23:59:59.000Z"
    )
)
```

### `by_updated_at(min_updated_at: Union[str, datetime], max_updated_at: Union[str, datetime])`
Filter by update date range.

**Args:**
- `min_updated_at` (Union[str, datetime]): The minimum update date (inclusive)
- `max_updated_at` (Union[str, datetime]): The maximum update date (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_updated_at(
        min_updated_at="2023-01-01T00:00:00.000Z",
        max_updated_at="2023-12-31T23:59:59.000Z"
    )
)
```

### `by_locked_at(min_locked_at: Union[str, datetime], max_locked_at: Union[str, datetime])`
Filter by lock date range.

**Args:**
- `min_locked_at` (Union[str, datetime]): The minimum lock date (inclusive)
- `max_locked_at` (Union[str, datetime]): The maximum lock date (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_locked_at(
        min_locked_at="2023-11-01T00:00:00.000Z",
        max_locked_at="2023-11-30T23:59:59.000Z"
    )
)
```

### `by_closed_at(min_closed_at: Union[str, datetime], max_closed_at: Union[str, datetime])`
Filter by close date range.

**Args:**
- `min_closed_at` (Union[str, datetime]): The minimum close date (inclusive)
- `max_closed_at` (Union[str, datetime]): The maximum close date (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_closed_at(
        min_closed_at="2023-11-01T00:00:00.000Z",
        max_closed_at="2023-11-30T23:59:59.000Z"
    )
)
```

### `by_final_mark(min_final_mark: Union[str, int], max_final_mark: Union[str, int])`
Filter by final mark range.

**Args:**
- `min_final_mark` (Union[str, int]): The minimum final mark value (inclusive)
- `max_final_mark` (Union[str, int]): The maximum final mark value (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_final_mark(min_final_mark=80, max_final_mark=125)
)
```

### `by_repo_url(min_repo_url: str, max_repo_url: str)`
Filter by repository URL range.

**Args:**
- `min_repo_url` (str): The minimum repository URL value (inclusive)
- `max_repo_url` (str): The maximum repository URL value (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_repo_url(min_repo_url="git@a", max_repo_url="git@z")
)
```

### `by_repo_uuid(min_repo_uuid: str, max_repo_uuid: str)`
Filter by repository UUID range.

**Args:**
- `min_repo_uuid` (str): The minimum repository UUID value (inclusive)
- `max_repo_uuid` (str): The maximum repository UUID value (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_repo_uuid(min_repo_uuid="a", max_repo_uuid="z")
)
```

### `by_deadline_at(min_deadline_at: Union[str, datetime], max_deadline_at: Union[str, datetime])`
Filter by deadline date range.

**Args:**
- `min_deadline_at` (Union[str, datetime]): The minimum deadline date (inclusive)
- `max_deadline_at` (Union[str, datetime]): The maximum deadline date (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_deadline_at(
        min_deadline_at="2023-12-01T00:00:00.000Z",
        max_deadline_at="2023-12-31T23:59:59.000Z"
    )
)
```

### `by_terminating_at(min_terminating_at: Union[str, datetime], max_terminating_at: Union[str, datetime])`
Filter by terminating date range.

**Args:**
- `min_terminating_at` (Union[str, datetime]): The minimum terminating date (inclusive)
- `max_terminating_at` (Union[str, datetime]): The maximum terminating date (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_terminating_at(
        min_terminating_at="2023-12-01T00:00:00.000Z",
        max_terminating_at="2023-12-31T23:59:59.000Z"
    )
)
```

### `by_project_session_id(min_project_session_id: Union[str, int], max_project_session_id: Union[str, int])`
Filter by project session ID range.

**Args:**
- `min_project_session_id` (Union[str, int]): The minimum project session ID value (inclusive)
- `max_project_session_id` (Union[str, int]): The maximum project session ID value (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_project_session_id(min_project_session_id=5000, max_project_session_id=6000)
)
```

### `by_status(min_status: str, max_status: str)`
Filter by status range.

**Args:**
- `min_status` (str): The minimum status value (inclusive)
- `max_status` (str): The maximum status value (inclusive)

**Example:**
```python
teams = client.teams.get_all(
    TeamParameters.Range.by_status(min_status="a", max_status="z")
)
```

# Cursus User Parameters

This module provides filtering, sorting, ranging, and custom parameters for cursus user queries.

## Overview

The Cursus User Parameters module allows you to:
- **Filter** cursus users by specific field values
- **Sort** cursus users by any field in ascending or descending order
- **Range** cursus users by numeric or date field boundaries
- **Custom Parameters** for additional filtering options (user_id, cursus_id)

## Usage

```python
from fortytwo import Client
from fortytwo.resources.cursus_user import CursusUserParameters
from fortytwo.request.parameter.parameter import SortDirection

client = Client(
    ...
)

# Filter by active status
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_active(True)
)

# Sort by level
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Sort.by_level(direction=SortDirection.DESCENDING)
)

# Range by creation date
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Range.by_created_at(
        min_created_at="2023-01-01T00:00:00Z",
        max_created_at="2023-12-31T23:59:59Z"
    )
)

# Use custom parameters
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Parameter.user_id("lhutt"),
    CursusUserParameters.Parameter.cursus_id(21)
)

# Combine multiple parameters
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_active(True),
    CursusUserParameters.Sort.by_level(direction=SortDirection.DESCENDING),
    CursusUserParameters.Parameter.cursus_id(21)
)
```

---

## Custom Parameters

Custom parameters for cursus user-specific filtering.

### `Parameter.user_id(user_id: Union[str, int])`
The user id or slug.

**Args:**
- `user_id` (Union[str, int]): The user id or slug

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Parameter.user_id("lhutt")
)
```

### `Parameter.cursus_id(cursus_id: Union[str, int])`
The cursus id or slug.

**Args:**
- `cursus_id` (Union[str, int]): The cursus id or slug

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Parameter.cursus_id(21)
)
```

---

## Filter Parameters

Filter cursus users by specific field values.

### `by_id(cursus_user_id: Union[str, int])`
Filter by cursus user ID.

**Args:**
- `cursus_user_id` (Union[str, int]): The cursus user ID

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_id(213072)
)
```

### `by_cursus_id(cursus_id: Union[str, int])`
Filter by cursus ID.

**Args:**
- `cursus_id` (Union[str, int]): The cursus ID

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_cursus_id(21)
)
```

### `by_user_id(user_id: Union[str, int])`
Filter by user ID.

**Args:**
- `user_id` (Union[str, int]): The user ID

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_user_id(132246)
)
```

### `by_created_at(created_at: Union[str, datetime])`
Filter by creation date.

**Args:**
- `created_at` (Union[str, datetime]): The creation date (ISO format string or datetime object)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_created_at("2023-04-01T03:26:43.172Z")
)
```

### `by_updated_at(updated_at: Union[str, datetime])`
Filter by update date.

**Args:**
- `updated_at` (Union[str, datetime]): The update date (ISO format string or datetime object)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_updated_at("2023-04-01T03:26:43.172Z")
)
```

### `by_end_at(end_at: Union[str, datetime])`
Filter by end date.

**Args:**
- `end_at` (Union[str, datetime]): The end date (ISO format string or datetime object)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_end_at("2023-12-31T23:00:00.000Z")
)
```

### `by_begin_at(begin_at: Union[str, datetime])`
Filter by begin date.

**Args:**
- `begin_at` (Union[str, datetime]): The begin date (ISO format string or datetime object)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_begin_at("2023-04-01T07:00:00.000Z")
)
```

### `by_has_coalition(has_coalition: bool)`
Filter by coalition status.

**Args:**
- `has_coalition` (bool): Whether the user has a coalition

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_has_coalition(True)
)
```

### `by_blackholed_at(blackholed_at: Union[str, datetime])`
Filter by blackhole date.

**Args:**
- `blackholed_at` (Union[str, datetime]): The blackhole date (ISO format string or datetime object)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_blackholed_at("2024-06-15T00:00:00.000Z")
)
```

### `by_level(level: Union[str, float])`
Filter by level.

**Args:**
- `level` (Union[str, float]): The level

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_level(21.42)
)
```

### `by_active(active: bool)`
Filter by active status.

**Args:**
- `active` (bool): Whether the cursus user is active

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_active(True)
)
```

### `by_campus_id(campus_id: Union[str, int])`
Filter by campus ID.

**Args:**
- `campus_id` (Union[str, int]): The campus ID

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_campus_id(1)
)
```

### `by_end(end: bool)`
Filter by end status.

**Args:**
- `end` (bool): Whether the cursus has ended

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_end(False)
)
```

### `by_future(future: bool)`
Filter by future status.

**Args:**
- `future` (bool): Whether the cursus is in the future

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_future(False)
)
```

### `by_blackholed(blackholed: bool)`
Filter by blackholed status.

**Args:**
- `blackholed` (bool): Whether the user is blackholed

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Filter.by_blackholed(False)
)
```

---

## Sort Parameters

Sort cursus users by any field in ascending or descending order using the `SortDirection` enum.

### `by_id(direction: SortDirection = SortDirection.DESCENDING)`
Sort by cursus user ID.

**Args:**
- `direction` (SortDirection): Sort direction (SortDirection.ASCENDING or SortDirection.DESCENDING)

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Sort.by_id(direction=SortDirection.DESCENDING)
)
```

### `by_cursus_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by cursus ID.

**Args:**
- `direction` (SortDirection): Sort direction (SortDirection.ASCENDING or SortDirection.DESCENDING)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Sort.by_cursus_id(direction=SortDirection.ASCENDING)
)
```

### `by_user_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by user ID.

**Args:**
- `direction` (SortDirection): Sort direction (SortDirection.ASCENDING or SortDirection.DESCENDING)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Sort.by_user_id(direction=SortDirection.ASCENDING)
)
```

### `by_created_at(direction: SortDirection = SortDirection.DESCENDING)`
Sort by creation date.

**Args:**
- `direction` (SortDirection): Sort direction (SortDirection.ASCENDING or SortDirection.DESCENDING)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Sort.by_created_at(direction=SortDirection.DESCENDING)
)
```

### `by_updated_at(direction: SortDirection = SortDirection.DESCENDING)`
Sort by update date.

**Args:**
- `direction` (SortDirection): Sort direction (SortDirection.ASCENDING or SortDirection.DESCENDING)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Sort.by_updated_at(direction=SortDirection.DESCENDING)
)
```

### `by_end_at(direction: SortDirection = SortDirection.ASCENDING)`
Sort by end date.

**Args:**
- `direction` (SortDirection): Sort direction (SortDirection.ASCENDING or SortDirection.DESCENDING)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Sort.by_end_at(direction=SortDirection.ASCENDING)
)
```

### `by_begin_at(direction: SortDirection = SortDirection.ASCENDING)`
Sort by begin date.

**Args:**
- `direction` (SortDirection): Sort direction (SortDirection.ASCENDING or SortDirection.DESCENDING)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Sort.by_begin_at(direction=SortDirection.ASCENDING)
)
```

### `by_has_coalition(direction: SortDirection = SortDirection.ASCENDING)`
Sort by coalition status.

**Args:**
- `direction` (SortDirection): Sort direction (SortDirection.ASCENDING or SortDirection.DESCENDING)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Sort.by_has_coalition(direction=SortDirection.ASCENDING)
)
```

### `by_blackholed_at(direction: SortDirection = SortDirection.ASCENDING)`
Sort by blackhole date.

**Args:**
- `direction` (SortDirection): Sort direction (SortDirection.ASCENDING or SortDirection.DESCENDING)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Sort.by_blackholed_at(direction=SortDirection.ASCENDING)
)
```

### `by_level(direction: SortDirection = SortDirection.DESCENDING)`
Sort by level.

**Args:**
- `direction` (SortDirection): Sort direction (SortDirection.ASCENDING or SortDirection.DESCENDING)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Sort.by_level(direction=SortDirection.DESCENDING)
)
```

---

## Range Parameters

Filter cursus users by numeric or date field boundaries.

### `by_id(min_id: Union[str, int], max_id: Union[str, int])`
Filter by ID range.

**Args:**
- `min_id` (Union[str, int]): The minimum ID value (inclusive)
- `max_id` (Union[str, int]): The maximum ID value (inclusive)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Range.by_id(min_id=200000, max_id=300000)
)
```

### `by_cursus_id(min_cursus_id: Union[str, int], max_cursus_id: Union[str, int])`
Filter by cursus ID range.

**Args:**
- `min_cursus_id` (Union[str, int]): The minimum cursus ID value (inclusive)
- `max_cursus_id` (Union[str, int]): The maximum cursus ID value (inclusive)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Range.by_cursus_id(min_cursus_id=1, max_cursus_id=21)
)
```

### `by_user_id(min_user_id: Union[str, int], max_user_id: Union[str, int])`
Filter by user ID range.

**Args:**
- `min_user_id` (Union[str, int]): The minimum user ID value (inclusive)
- `max_user_id` (Union[str, int]): The maximum user ID value (inclusive)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Range.by_user_id(min_user_id=100000, max_user_id=150000)
)
```

### `by_created_at(min_created_at: Union[str, datetime], max_created_at: Union[str, datetime])`
Filter by creation date range.

**Args:**
- `min_created_at` (Union[str, datetime]): The minimum creation date (inclusive)
- `max_created_at` (Union[str, datetime]): The maximum creation date (inclusive)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Range.by_created_at(
        min_created_at="2023-01-01T00:00:00Z",
        max_created_at="2023-12-31T23:59:59Z"
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
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Range.by_updated_at(
        min_updated_at="2023-01-01T00:00:00Z",
        max_updated_at="2023-12-31T23:59:59Z"
    )
)
```

### `by_end_at(min_end_at: Union[str, datetime], max_end_at: Union[str, datetime])`
Filter by end date range.

**Args:**
- `min_end_at` (Union[str, datetime]): The minimum end date (inclusive)
- `max_end_at` (Union[str, datetime]): The maximum end date (inclusive)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Range.by_end_at(
        min_end_at="2023-01-01T00:00:00Z",
        max_end_at="2023-12-31T23:59:59Z"
    )
)
```

### `by_begin_at(min_begin_at: Union[str, datetime], max_begin_at: Union[str, datetime])`
Filter by begin date range.

**Args:**
- `min_begin_at` (Union[str, datetime]): The minimum begin date (inclusive)
- `max_begin_at` (Union[str, datetime]): The maximum begin date (inclusive)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Range.by_begin_at(
        min_begin_at="2023-01-01T00:00:00Z",
        max_begin_at="2023-12-31T23:59:59Z"
    )
)
```

### `by_has_coalition(min_has_coalition: bool, max_has_coalition: bool)`
Filter by coalition status range.

**Args:**
- `min_has_coalition` (bool): The minimum coalition status (inclusive)
- `max_has_coalition` (bool): The maximum coalition status (inclusive)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Range.by_has_coalition(
        min_has_coalition=False,
        max_has_coalition=True
    )
)
```

### `by_blackholed_at(min_blackholed_at: Union[str, datetime], max_blackholed_at: Union[str, datetime])`
Filter by blackhole date range.

**Args:**
- `min_blackholed_at` (Union[str, datetime]): The minimum blackhole date (inclusive)
- `max_blackholed_at` (Union[str, datetime]): The maximum blackhole date (inclusive)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Range.by_blackholed_at(
        min_blackholed_at="2024-01-01T00:00:00Z",
        max_blackholed_at="2024-12-31T23:59:59Z"
    )
)
```

### `by_level(min_level: Union[str, float], max_level: Union[str, float])`
Filter by level range.

**Args:**
- `min_level` (Union[str, float]): The minimum level value (inclusive)
- `max_level` (Union[str, float]): The maximum level value (inclusive)

**Example:**
```python
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Range.by_level(min_level=0.0, max_level=21.0)
)
```

---

## Combining Parameters

You can combine multiple parameters to create complex queries:

```python
# Get active cursus users in a specific cursus, sorted by level, within a date range
cursus_users = client.cursus_users.get_all(
    CursusUserParameters.Parameter.cursus_id(21),
    CursusUserParameters.Filter.by_active(True),
    CursusUserParameters.Sort.by_level(direction=SortDirection.DESCENDING),
    CursusUserParameters.Range.by_created_at(
        min_created_at="2023-01-01T00:00:00Z",
        max_created_at="2023-12-31T23:59:59Z"
    )
)
```

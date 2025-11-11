# Campus User Parameters

This module provides filtering, sorting, ranging, and custom parameters for campus user queries.

## Overview

The Campus User Parameters module allows you to:
- **Filter** campus users by specific field values
- **Sort** campus users by any field in ascending or descending order
- **Range** campus users by numeric or date field boundaries
- **Custom Parameters** for additional filtering options (user_id)

## Usage

```python
from fortytwo import Client
from fortytwo.resources.campus_user.parameter import CampusUserParameters
from fortytwo.request.parameter.parameter import SortDirection

client = Client(
    ...
)

# Filter by primary status
campus_users = client.campus_users.get_all(
    CampusUserParameters.Filter.by_is_primary(True)
)

# Sort by campus ID
campus_users = client.campus_users.get_all(
    CampusUserParameters.Sort.by_campus_id(direction=SortDirection.ASCENDING)
)

# Range by creation date
campus_users = client.campus_users.get_all(
    CampusUserParameters.Range.created_at_range(
        start_date="2023-01-01T00:00:00Z",
        end_date="2023-12-31T23:59:59Z"
    )
)

# Use custom parameters
campus_users = client.campus_users.get_all(
    CampusUserParameters.Parameter.user_id("lhutt")
)

# Combine multiple parameters
campus_users = client.campus_users.get_all(
    CampusUserParameters.Filter.by_is_primary(True),
    CampusUserParameters.Sort.by_created_at(direction=SortDirection.DESCENDING),
    CampusUserParameters.Parameter.user_id(132246)
)
```

---

## Custom Parameters

Custom parameters for campus user-specific filtering.

### `Parameter.user_id(user_id: Union[str, int])`
The user id or slug.

**Args:**
- `user_id` (Union[str, int]): The user id or slug

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Parameter.user_id("lhutt")
)
```

---

## Filter Parameters

Filter campus users by specific field values.

### `Filter.by_id(campus_user_id: Union[str, int])`
Filter by campus user ID.

**Args:**
- `campus_user_id` (Union[str, int]): The campus user ID

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Filter.by_id(123641)
)
```

### `Filter.by_user_id(user_id: Union[str, int])`
Filter by user ID.

**Args:**
- `user_id` (Union[str, int]): The user ID

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Filter.by_user_id(132246)
)
```

### `Filter.by_campus_id(campus_id: Union[str, int])`
Filter by campus ID.

**Args:**
- `campus_id` (Union[str, int]): The campus ID

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Filter.by_campus_id(48)
)
```

### `Filter.by_is_primary(is_primary: bool)`
Filter by primary status.

**Args:**
- `is_primary` (bool): Whether this is the primary campus for the user

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Filter.by_is_primary(True)
)
```

### `Filter.by_created_at(created_at: Union[str, datetime])`
Filter by creation date.

**Args:**
- `created_at` (Union[str, datetime]): The creation date (ISO format string or datetime object)

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Filter.by_created_at("2022-08-26T09:32:41.354Z")
)
```

### `Filter.by_updated_at(updated_at: Union[str, datetime])`
Filter by update date.

**Args:**
- `updated_at` (Union[str, datetime]): The update date (ISO format string or datetime object)

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Filter.by_updated_at("2022-08-26T09:32:41.354Z")
)
```

---

## Sort Parameters

Sort campus users by any field. All methods accept a `direction` parameter.

**Import:**
```python
from fortytwo.request.parameter.parameter import Sort, SortDirection
```

### `Sort.by_id(direction: SortDirection = SortDirection.DESCENDING)`
Sort by campus user ID (default descending).

**Args:**
- `direction` (SortDirection): Sort direction (ASCENDING or DESCENDING)

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Sort.by_id(direction=SortDirection.DESCENDING)
)
```

### `Sort.by_user_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by user ID.

**Args:**
- `direction` (SortDirection): Sort direction (ASCENDING or DESCENDING)

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Sort.by_user_id(direction=SortDirection.ASCENDING)
)
```

### `Sort.by_campus_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by campus ID.

**Args:**
- `direction` (SortDirection): Sort direction (ASCENDING or DESCENDING)

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Sort.by_campus_id(direction=SortDirection.ASCENDING)
)
```

### `Sort.by_is_primary(direction: SortDirection = SortDirection.DESCENDING)`
Sort by primary status.

**Args:**
- `direction` (SortDirection): Sort direction (ASCENDING or DESCENDING)

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Sort.by_is_primary(direction=SortDirection.DESCENDING)
)
```

### `Sort.by_created_at(direction: SortDirection = SortDirection.DESCENDING)`
Sort by creation date (default descending).

**Args:**
- `direction` (SortDirection): Sort direction (ASCENDING or DESCENDING)

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Sort.by_created_at(direction=SortDirection.DESCENDING)
)
```

### `Sort.by_updated_at(direction: SortDirection = SortDirection.DESCENDING)`
Sort by update date (default descending).

**Args:**
- `direction` (SortDirection): Sort direction (ASCENDING or DESCENDING)

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Sort.by_updated_at(direction=SortDirection.DESCENDING)
)
```

---

## Range Parameters

Range campus users by field boundaries. All range methods accept optional min and max values.

### `Range.id_range(min_id: Union[str, int, None] = None, max_id: Union[str, int, None] = None)`
Filter by campus user ID range.

**Args:**
- `min_id` (Union[str, int], optional): Minimum ID value
- `max_id` (Union[str, int], optional): Maximum ID value

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Range.id_range(min_id=100000, max_id=200000)
)
```

### `Range.user_id_range(min_user_id: Union[str, int, None] = None, max_user_id: Union[str, int, None] = None)`
Filter by user ID range.

**Args:**
- `min_user_id` (Union[str, int], optional): Minimum user ID value
- `max_user_id` (Union[str, int], optional): Maximum user ID value

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Range.user_id_range(min_user_id=100000, max_user_id=200000)
)
```

### `Range.campus_id_range(min_campus_id: Union[str, int, None] = None, max_campus_id: Union[str, int, None] = None)`
Filter by campus ID range.

**Args:**
- `min_campus_id` (Union[str, int], optional): Minimum campus ID value
- `max_campus_id` (Union[str, int], optional): Maximum campus ID value

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Range.campus_id_range(min_campus_id=1, max_campus_id=50)
)
```

### `Range.is_primary_range(min_is_primary: bool | None = None, max_is_primary: bool | None = None)`
Filter by primary status range.

**Args:**
- `min_is_primary` (bool, optional): Minimum primary status
- `max_is_primary` (bool, optional): Maximum primary status

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Range.is_primary_range(min_is_primary=True, max_is_primary=True)
)
```

### `Range.created_at_range(start_date: Union[str, datetime, None] = None, end_date: Union[str, datetime, None] = None)`
Filter by creation date range.

**Args:**
- `start_date` (Union[str, datetime], optional): Start date (ISO format string or datetime object)
- `end_date` (Union[str, datetime], optional): End date (ISO format string or datetime object)

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Range.created_at_range(
        start_date="2022-01-01T00:00:00Z",
        end_date="2022-12-31T23:59:59Z"
    )
)
```

### `Range.updated_at_range(start_date: Union[str, datetime, None] = None, end_date: Union[str, datetime, None] = None)`
Filter by update date range.

**Args:**
- `start_date` (Union[str, datetime], optional): Start date (ISO format string or datetime object)
- `end_date` (Union[str, datetime], optional): End date (ISO format string or datetime object)

**Example:**
```python
campus_users = client.campus_users.get_all(
    CampusUserParameters.Range.updated_at_range(
        start_date="2022-01-01T00:00:00Z",
        end_date="2022-12-31T23:59:59Z"
    )
)
```

---

## Combining Parameters

You can combine multiple parameters for complex queries:

```python
from fortytwo.request.parameter.parameter import SortDirection

# Get primary campus users created in 2022, sorted by creation date
campus_users = client.campus_users.get_all(
    CampusUserParameters.Filter.by_is_primary(True),
    CampusUserParameters.Range.created_at_range(
        start_date="2022-01-01T00:00:00Z",
        end_date="2022-12-31T23:59:59Z"
    ),
    CampusUserParameters.Sort.by_created_at(direction=SortDirection.DESCENDING),
    page=1,
    page_size=50
)
```

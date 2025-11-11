# Location Parameters

This document describes all available parameters for filtering, sorting, and ranging Location resources in the 42 API.

## Overview

Location parameters allow you to customize queries to the 42 API's location endpoint. You can:
- **Filter** - Find locations matching specific criteria
- **Sort** - Order results by specific fields
- **Range** - Retrieve locations within a specific range of values

## Usage

```python
from fortytwo import Client, parameter
from fortytwo.request.parameter.parameter import SortDirection

client = Client(
    ...
)

# Using location-specific parameters
locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_user_id(12345),
    parameter.LocationParameters.Sort.by_begin_at(SortDirection.DESCENDING),
    parameter.PageSize(100)
)
```

## Filter Parameters

Filters narrow down results to match specific criteria.

### `by_id(location_id)`
Filter locations by their unique ID.

**Parameters:**
- `location_id` (str | int): The location ID to filter by

**Example:**
```python
locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_id(987654)
)
```

---

### `by_user_id(user_id)`
Filter locations by user ID.

**Parameters:**
- `user_id` (str | int): The user ID to filter by

**Example:**
```python
# Get all locations for a specific user
user_locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_user_id(12345)
)
```

---

### `by_begin_at(begin_at)`
Filter locations by their begin date/time.

**Parameters:**
- `begin_at` (str | datetime): The begin date (ISO format string or datetime object)

**Example:**
```python
from datetime import datetime

locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_begin_at("2024-01-15T08:00:00Z")
)
```

---

### `by_end_at(end_at)`
Filter locations by their end date/time.

**Parameters:**
- `end_at` (str | datetime): The end date (ISO format string or datetime object)

**Example:**
```python
locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_end_at("2024-01-15T18:00:00Z")
)
```

---

### `by_primary(primary)`
Filter locations by primary status (whether it's the user's primary location).

**Parameters:**
- `primary` (str | bool): Primary status (True/False or "true"/"false")

**Example:**
```python
# Get only primary locations
primary_locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_primary(True)
)

# Get non-primary locations
secondary_locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_primary(False)
)
```

---

### `by_host(host)`
Filter locations by host/computer name.

**Parameters:**
- `host` (str): The host name to filter by

**Example:**
```python
# Find who's at a specific computer
locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_host("e1r1p1")
)
```

---

### `by_campus_id(campus_id)`
Filter locations by campus ID.

**Parameters:**
- `campus_id` (str | int): The campus ID

**Example:**
```python
# Get all current locations at Paris campus (ID: 1)
paris_locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_campus_id(1)
)
```

---

## Sort Parameters

Sort parameters order the results by specific fields.

> **Note**: All sort methods use the `SortDirection` enum to specify ascending or descending order. Import it with:
> ```python
> from fortytwo.request.parameter.parameter import SortDirection
> ```

### `by_id(direction=SortDirection.DESCENDING)`
Sort by location ID.

**Default:** Descending (newest first)

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

# Newest locations first (default)
locations = client.locations.get_all(
    parameter.LocationParameters.Sort.by_id()
)

# Oldest locations first
locations = client.locations.get_all(
    parameter.LocationParameters.Sort.by_id(SortDirection.ASCENDING)
)
```

---

### `by_user_id(direction=SortDirection.ASCENDING)`
Sort by user ID.

**Default:** Ascending (lowest ID first)

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

locations = client.locations.get_all(
    parameter.LocationParameters.Sort.by_user_id()
)
```

---

### `by_begin_at(direction=SortDirection.DESCENDING)`
Sort by begin date/time.

**Default:** Descending (most recent first)

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

# Most recent sessions first (default)
locations = client.locations.get_all(
    parameter.LocationParameters.Sort.by_begin_at()
)

# Oldest sessions first
locations = client.locations.get_all(
    parameter.LocationParameters.Sort.by_begin_at(SortDirection.ASCENDING)
)
```

---

### `by_end_at(direction=SortDirection.DESCENDING)`
Sort by end date/time.

**Default:** Descending (most recent first)

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

# Sort by when sessions ended (default)
locations = client.locations.get_all(
    parameter.LocationParameters.Sort.by_end_at()
)
```

---

### `by_primary(direction=SortDirection.DESCENDING)`
Sort by primary status.

**Default:** Descending (primary locations first)

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

# Primary locations first (default)
locations = client.locations.get_all(
    parameter.LocationParameters.Sort.by_primary()
)
```

---

### `by_host(direction=SortDirection.ASCENDING)`
Sort alphabetically by host/computer name.

**Default:** Ascending (A-Z)

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

# A-Z (default)
locations = client.locations.get_all(
    parameter.LocationParameters.Sort.by_host()
)

# Z-A
locations = client.locations.get_all(
    parameter.LocationParameters.Sort.by_host(SortDirection.DESCENDING)
)
```

---

### `by_campus_id(direction=SortDirection.ASCENDING)`
Sort by campus ID.

**Default:** Ascending (lowest ID first)

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

locations = client.locations.get_all(
    parameter.LocationParameters.Sort.by_campus_id()
)
```

---

## Range Parameters

Range parameters retrieve locations with values between a minimum and maximum.

All range methods accept optional `min` and `max` parameters. You can specify one or both.

### `id_range(min_id=None, max_id=None)`
Filter locations with IDs in a specific range.

**Parameters:**
- `min_id` (str | int, optional): Minimum ID (inclusive)
- `max_id` (str | int, optional): Maximum ID (inclusive)

**Example:**
```python
# Locations with IDs between 1000 and 2000
locations = client.locations.get_all(
    parameter.LocationParameters.Range.id_range(1000, 2000)
)

# Locations with ID 1000 or greater
locations = client.locations.get_all(
    parameter.LocationParameters.Range.id_range(min_id=1000)
)
```

---

### `user_id_range(min_user_id=None, max_user_id=None)`
Filter locations with user IDs in a specific range.

**Parameters:**
- `min_user_id` (str | int, optional): Minimum user ID (inclusive)
- `max_user_id` (str | int, optional): Maximum user ID (inclusive)

**Example:**
```python
# Locations for users with IDs 10000-20000
locations = client.locations.get_all(
    parameter.LocationParameters.Range.user_id_range(10000, 20000)
)
```

---

### `begin_at_range(start_date=None, end_date=None)`
Filter locations that began within a date range.

**Parameters:**
- `start_date` (str | datetime, optional): Start date (inclusive)
- `end_date` (str | datetime, optional): End date (inclusive)

**Example:**
```python
from datetime import datetime

# Locations that began today
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
tomorrow = today + timedelta(days=1)

locations = client.locations.get_all(
    parameter.LocationParameters.Range.begin_at_range(today, tomorrow)
)

# Locations that began in the last hour
one_hour_ago = datetime.now() - timedelta(hours=1)
locations = client.locations.get_all(
    parameter.LocationParameters.Range.begin_at_range(start_date=one_hour_ago)
)
```

---

### `end_at_range(start_date=None, end_date=None)`
Filter locations that ended within a date range.

**Parameters:**
- `start_date` (str | datetime, optional): Start date (inclusive)
- `end_date` (str | datetime, optional): End date (inclusive)

**Example:**
```python
from datetime import datetime, timedelta

# Locations that ended in the last 24 hours
yesterday = datetime.now() - timedelta(days=1)

locations = client.locations.get_all(
    parameter.LocationParameters.Range.end_at_range(start_date=yesterday)
)
```

---

### `host_range(min_host=None, max_host=None)`
Filter locations with hosts in alphabetical range.

**Parameters:**
- `min_host` (str, optional): Minimum host (inclusive)
- `max_host` (str, optional): Maximum host (inclusive)

**Example:**
```python
# Hosts starting with 'e1'
locations = client.locations.get_all(
    parameter.LocationParameters.Range.host_range("e1r1p1", "e1r9p99")
)
```

---

### `campus_id_range(min_campus_id=None, max_campus_id=None)`
Filter locations with campus IDs in a specific range.

**Parameters:**
- `min_campus_id` (str | int, optional): Minimum campus ID (inclusive)
- `max_campus_id` (str | int, optional): Maximum campus ID (inclusive)

**Example:**
```python
locations = client.locations.get_all(
    parameter.LocationParameters.Range.campus_id_range(1, 10)
)
```

---

## Combining Parameters

You can combine multiple parameters to create complex queries:

```python
from datetime import datetime, timedelta
from fortytwo.request.parameter.parameter import SortDirection

# Get current active locations at a specific campus
now = datetime.now()
locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_campus_id(1),
    parameter.LocationParameters.Range.begin_at_range(end_date=now),
    parameter.LocationParameters.Range.end_at_range(start_date=now),
    parameter.LocationParameters.Sort.by_begin_at(SortDirection.DESCENDING),
    parameter.PageSize(100)
)

# Find who's been at specific computers in the last hour
one_hour_ago = datetime.now() - timedelta(hours=1)
recent_locations = client.locations.get_all(
    parameter.LocationParameters.Range.host_range("e1r1p1", "e1r1p20"),
    parameter.LocationParameters.Range.begin_at_range(start_date=one_hour_ago),
    parameter.LocationParameters.Sort.by_begin_at(SortDirection.DESCENDING)
)

# Get a user's primary location history
user_primary_locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_user_id(12345),
    parameter.LocationParameters.Filter.by_primary(True),
    parameter.LocationParameters.Sort.by_begin_at(SortDirection.DESCENDING),
    parameter.PageSize(50)
)
```

## Common Use Cases

### Find who's currently at a specific computer
```python
from fortytwo.request.parameter.parameter import SortDirection

locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_host("e1r1p1"),
    parameter.LocationParameters.Sort.by_begin_at(SortDirection.DESCENDING),
    parameter.PageSize(1)
)
current_user = locations[0] if locations and not locations[0].end_at else None
```

### Get all current locations at a campus
```python
from datetime import datetime

now = datetime.now()
current_locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_campus_id(1),
    parameter.LocationParameters.Range.begin_at_range(end_date=now),
    parameter.LocationParameters.Range.end_at_range(start_date=now),
    parameter.PageSize(200)
)
```

### Track a user's location history
```python
from fortytwo.request.parameter.parameter import SortDirection

user_locations = client.locations.get_all(
    parameter.LocationParameters.Filter.by_user_id(12345),
    parameter.LocationParameters.Sort.by_begin_at(SortDirection.DESCENDING),
    parameter.PageSize(100)
)
```

### Find active sessions in the last hour
```python
from datetime import datetime, timedelta
from fortytwo.request.parameter.parameter import SortDirection

one_hour_ago = datetime.now() - timedelta(hours=1)
recent_sessions = client.locations.get_all(
    parameter.LocationParameters.Range.begin_at_range(start_date=one_hour_ago),
    parameter.LocationParameters.Sort.by_begin_at(SortDirection.DESCENDING)
)
```

### Get locations in a specific row/area
```python
from fortytwo.request.parameter.parameter import SortDirection

# All computers in row 1
row1_locations = client.locations.get_all(
    parameter.LocationParameters.Range.host_range("e1r1p1", "e1r1p99"),
    parameter.LocationParameters.Sort.by_host()
)
```

### Find a user's primary location
```python
from fortytwo.request.parameter.parameter import SortDirection

primary_location = client.locations.get_all(
    parameter.LocationParameters.Filter.by_user_id(12345),
    parameter.LocationParameters.Filter.by_primary(True),
    parameter.LocationParameters.Sort.by_begin_at(SortDirection.DESCENDING),
    parameter.PageSize(1)
)
```

## Examples

See the [`example/`](../../../../example/) directory for complete working examples.

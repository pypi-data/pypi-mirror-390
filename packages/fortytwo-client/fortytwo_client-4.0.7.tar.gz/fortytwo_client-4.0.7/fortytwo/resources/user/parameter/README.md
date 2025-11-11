# User Parameters

This document describes all available parameters for filtering, sorting, and ranging User resources in the 42 API.

## Overview

User parameters allow you to customize queries to the 42 API's user endpoint. You can:
- **Filter** - Find users matching specific criteria
- **Sort** - Order results by specific fields
- **Range** - Retrieve users within a specific range of values

## Usage

```python
from fortytwo import Client, parameter
from fortytwo.request.parameter.parameter import SortDirection

client = Client(
    ...
)

# Using user-specific parameters
users = client.users.get_all(
    parameter.UserParameters.Filter.by_login("example"),
    parameter.UserParameters.Sort.by_created_at(SortDirection.DESCENDING),
    parameter.PageSize(50)
)
```

## Filter Parameters

Filters narrow down results to match specific criteria.

### `by_id(user_id)`
Filter users by their unique ID.

**Parameters:**
- `user_id` (str | int): The user ID to filter by

**Example:**
```python
users = client.users.get_all(
    parameter.UserParameters.Filter.by_id(12345)
)
```

---

### `by_login(login)`
Filter users by their login name.

**Parameters:**
- `login` (str): The login name to filter by

**Example:**
```python
users = client.users.get_all(
    parameter.UserParameters.Filter.by_login("jdoe")
)
```

---

### `by_email(email)`
Filter users by their email address.

**Parameters:**
- `email` (str): The email address to filter by

**Example:**
```python
users = client.users.get_all(
    parameter.UserParameters.Filter.by_email("john.doe@student.42.fr")
)
```

---

### `by_created_at(created_at)`
Filter users by their account creation date.

**Parameters:**
- `created_at` (str | datetime): The creation date (ISO format string or datetime object)

**Example:**
```python
from datetime import datetime

users = client.users.get_all(
    parameter.UserParameters.Filter.by_created_at("2024-01-01T00:00:00Z")
)

# Or with datetime object
users = client.users.get_all(
    parameter.UserParameters.Filter.by_created_at(datetime(2024, 1, 1))
)
```

---

### `by_updated_at(updated_at)`
Filter users by their last profile update date.

**Parameters:**
- `updated_at` (str | datetime): The update date (ISO format string or datetime object)

**Example:**
```python
users = client.users.get_all(
    parameter.UserParameters.Filter.by_updated_at("2024-10-01T00:00:00Z")
)
```

---

### `by_pool_year(year)`
Filter users by the year they attended the piscine (swimming pool).

**Parameters:**
- `year` (str | int): The pool year (e.g., 2024)

**Example:**
```python
# Get all users from the 2024 piscine
users = client.users.get_all(
    parameter.UserParameters.Filter.by_pool_year(2024)
)
```

---

### `by_pool_month(month)`
Filter users by the month they attended the piscine.

**Parameters:**
- `month` (str | int): The pool month (e.g., "july", "september", or numeric 7, 9)

**Example:**
```python
# Get users from the July piscine
users = client.users.get_all(
    parameter.UserParameters.Filter.by_pool_month("july")
)
```

---

### `by_kind(kind)`
Filter users by their type (student, staff, etc.).

**Parameters:**
- `kind` (str): The user kind/type

**Common values:**
- `"student"` - Regular students
- `"staff"` - 42 staff members
- `"admin"` - Administrators

**Example:**
```python
# Get all students
users = client.users.get_all(
    parameter.UserParameters.Filter.by_kind("student")
)
```

---

### `by_status(status)`
Filter users by their account status.

**Parameters:**
- `status` (str): The status to filter by

**Example:**
```python
users = client.users.get_all(
    parameter.UserParameters.Filter.by_status("active")
)
```

---

### `by_campus_id(campus_id)`
Filter users by their primary campus.

**Parameters:**
- `campus_id` (str | int): The campus ID

**Example:**
```python
# Get all users from Paris campus (ID: 1)
users = client.users.get_all(
    parameter.UserParameters.Filter.by_campus_id(1)
)
```

---

### `by_cursus_id(cursus_id)`
Filter users enrolled in a specific cursus.

**Parameters:**
- `cursus_id` (str | int): The cursus ID

**Example:**
```python
# Get users in the 42 cursus (ID: 21)
users = client.users.get_all(
    parameter.UserParameters.Filter.by_cursus_id(21)
)
```

---

## Sort Parameters

Sort parameters order the results by specific fields using the `SortDirection` enum.

All sort methods accept a `direction` parameter:
- `SortDirection.ASCENDING` - Ascending order (A-Z, 0-9, oldest-newest)
- `SortDirection.DESCENDING` - Descending order (Z-A, 9-0, newest-oldest)

### `by_id(direction=SortDirection.DESCENDING)`
Sort by user ID.

**Default:** Descending (newest users first)

**Example:**
```python
# Newest users first (default)
users = client.users.get_all(
    parameter.UserParameters.Sort.by_id()
)

# Oldest users first
users = client.users.get_all(
    parameter.UserParameters.Sort.by_id(SortDirection.ASCENDING)
)
```

---

### `by_login(direction=SortDirection.ASCENDING)`
Sort alphabetically by login.

**Default:** Ascending (A-Z)

**Example:**
```python
# A-Z
users = client.users.get_all(
    parameter.UserParameters.Sort.by_login()
)

# Z-A
users = client.users.get_all(
    parameter.UserParameters.Sort.by_login(SortDirection.DESCENDING)
)
```

---

### `by_email(direction=SortDirection.ASCENDING)`
Sort alphabetically by email.

**Default:** Ascending (A-Z)

**Example:**
```python
users = client.users.get_all(
    parameter.UserParameters.Sort.by_email()
)
```

---

### `by_created_at(direction=SortDirection.DESCENDING)`
Sort by account creation date.

**Default:** Descending (newest first)

**Example:**
```python
# Newest accounts first
users = client.users.get_all(
    parameter.UserParameters.Sort.by_created_at()
)

# Oldest accounts first
users = client.users.get_all(
    parameter.UserParameters.Sort.by_created_at(SortDirection.ASCENDING)
)
```

---

### `by_updated_at(direction=SortDirection.DESCENDING)`
Sort by last profile update date.

**Default:** Descending (most recently updated first)

**Example:**
```python
# Recently updated profiles first
users = client.users.get_all(
    parameter.UserParameters.Sort.by_updated_at()
)
```

---

### `by_first_name(direction=SortDirection.ASCENDING)`
Sort alphabetically by first name.

**Default:** Ascending (A-Z)

**Example:**
```python
users = client.users.get_all(
    parameter.UserParameters.Sort.by_first_name()
)
```

---

### `by_last_name(direction=SortDirection.ASCENDING)`
Sort alphabetically by last name.

**Default:** Ascending (A-Z)

**Example:**
```python
users = client.users.get_all(
    parameter.UserParameters.Sort.by_last_name()
)
```

---

### `by_pool_year(direction=SortDirection.DESCENDING)`
Sort by piscine year.

**Default:** Descending (most recent year first)

**Example:**
```python
users = client.users.get_all(
    parameter.UserParameters.Sort.by_pool_year()
)
```

---

### `by_pool_month(direction=SortDirection.DESCENDING)`
Sort by piscine month.

**Default:** Descending (most recent month first)

**Example:**
```python
users = client.users.get_all(
    parameter.UserParameters.Sort.by_pool_month()
)
```

---

## Range Parameters

Range parameters retrieve users with values between a minimum and maximum.

All range methods accept optional `min` and `max` parameters. You can specify one or both.

### `id_range(min_id=None, max_id=None)`
Filter users with IDs in a specific range.

**Parameters:**
- `min_id` (str | int, optional): Minimum ID (inclusive)
- `max_id` (str | int, optional): Maximum ID (inclusive)

**Example:**
```python
# Users with IDs between 1000 and 2000
users = client.users.get_all(
    parameter.UserParameters.Range.id_range(1000, 2000)
)

# Users with ID 1000 or greater
users = client.users.get_all(
    parameter.UserParameters.Range.id_range(min_id=1000)
)

# Users with ID 2000 or less
users = client.users.get_all(
    parameter.UserParameters.Range.id_range(max_id=2000)
)
```

---

### `login_range(min_login=None, max_login=None)`
Filter users with logins in alphabetical range.

**Parameters:**
- `min_login` (str, optional): Minimum login (inclusive)
- `max_login` (str, optional): Maximum login (inclusive)

**Example:**
```python
# Users with logins from 'a' to 'm'
users = client.users.get_all(
    parameter.UserParameters.Range.login_range("a", "m")
)
```

---

### `email_range(min_email=None, max_email=None)`
Filter users with emails in alphabetical range.

**Parameters:**
- `min_email` (str, optional): Minimum email (inclusive)
- `max_email` (str, optional): Maximum email (inclusive)

**Example:**
```python
users = client.users.get_all(
    parameter.UserParameters.Range.email_range("a@", "m@")
)
```

---

### `created_at_range(start_date=None, end_date=None)`
Filter users created within a date range.

**Parameters:**
- `start_date` (str | datetime, optional): Start date (inclusive)
- `end_date` (str | datetime, optional): End date (inclusive)

**Example:**
```python
from datetime import datetime

# Users created in 2024
users = client.users.get_all(
    parameter.UserParameters.Range.created_at_range(
        datetime(2024, 1, 1),
        datetime(2024, 12, 31)
    )
)

# Users created after a specific date
users = client.users.get_all(
    parameter.UserParameters.Range.created_at_range(
        start_date="2024-01-01T00:00:00Z"
    )
)
```

---

### `updated_at_range(start_date=None, end_date=None)`
Filter users updated within a date range.

**Parameters:**
- `start_date` (str | datetime, optional): Start date (inclusive)
- `end_date` (str | datetime, optional): End date (inclusive)

**Example:**
```python
# Users updated in the last month
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=30)

users = client.users.get_all(
    parameter.UserParameters.Range.updated_at_range(start_date, end_date)
)
```

---

### `pool_year_range(min_year=None, max_year=None)`
Filter users by piscine year range.

**Parameters:**
- `min_year` (str | int, optional): Minimum year (inclusive)
- `max_year` (str | int, optional): Maximum year (inclusive)

**Example:**
```python
# Users from piscines between 2020 and 2024
users = client.users.get_all(
    parameter.UserParameters.Range.pool_year_range(2020, 2024)
)
```

---

## Combining Parameters

You can combine multiple parameters to create complex queries:

```python
from datetime import datetime
from fortytwo.request.parameter.parameter import SortDirection

# Get all students from the 2024 July piscine,
# sorted by creation date, with pagination
users = client.users.get_all(
    parameter.UserParameters.Filter.by_kind("student"),
    parameter.UserParameters.Filter.by_pool_year(2024),
    parameter.UserParameters.Filter.by_pool_month("july"),
    parameter.UserParameters.Sort.by_created_at(SortDirection.DESCENDING),
    parameter.PageSize(50),
    parameter.PageNumber(1)
)

# Get users created in 2024, sorted by login
users = client.users.get_all(
    parameter.UserParameters.Range.created_at_range(
        datetime(2024, 1, 1),
        datetime(2024, 12, 31)
    ),
    parameter.UserParameters.Sort.by_login(SortDirection.ASCENDING)
)

# Get users from a specific campus with IDs in a range
users = client.users.get_all(
    parameter.UserParameters.Filter.by_campus_id(1),
    parameter.UserParameters.Range.id_range(1000, 2000)
)
```

## Common Use Cases

### Find a specific user by login
```python
users = client.users.get_all(
    parameter.UserParameters.Filter.by_login("jdoe")
)
user = users[0] if users else None
```

### Get all students from a specific piscine
```python
students = client.users.get_all(
    parameter.UserParameters.Filter.by_kind("student"),
    parameter.UserParameters.Filter.by_pool_year(2024),
    parameter.UserParameters.Filter.by_pool_month("july"),
    parameter.UserParameters.Sort.by_login()
)
```

### Get recently updated profiles
```python
from datetime import datetime, timedelta
from fortytwo.request.parameter.parameter import SortDirection

cutoff_date = datetime.now() - timedelta(days=7)

recent_users = client.users.get_all(
    parameter.UserParameters.Range.updated_at_range(start_date=cutoff_date),
    parameter.UserParameters.Sort.by_updated_at(SortDirection.DESCENDING),
    parameter.PageSize(100)
)
```

### Get all users from a specific campus
```python
campus_users = client.users.get_all(
    parameter.UserParameters.Filter.by_campus_id(1),
    parameter.UserParameters.Sort.by_login(),
    parameter.PageSize(100)
)
```

## Examples

See the [`example/`](../../../../example/) directory for complete working examples.

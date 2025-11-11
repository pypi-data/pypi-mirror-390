# Campus User Resource

The Campus User resource provides access to campus user data from the 42 API.

## Overview

This module allows you to fetch campus user information from the 42 API, representing a user's association with a specific campus. This includes their primary campus designation and registration details.

## Classes

### `CampusUser`
Represents a user's association with a specific campus.

**Properties:**
- `id` (int): Campus user's unique identifier
- `user_id` (int): ID of the user
- `campus_id` (int): ID of the campus
- `is_primary` (bool): Whether this is the user's primary campus
- `created_at` (datetime): When the campus user entry was created
- `updated_at` (datetime): When the campus user entry was last updated

### Resource Classes

#### `GetCampusUsers`
Fetches all campus users with optional filtering.
- **Endpoint:** `/campus_users`
- **Method:** GET
- **Returns:** `List[CampusUser]`

#### `GetCampusUserById`
Fetches a single campus user by their ID.
- **Endpoint:** `/campus_users/{id}`
- **Method:** GET
- **Returns:** `CampusUser`

#### `GetCampusUsersByUserId`
Fetches all campus users for a specific user.
- **Endpoint:** `/users/{user_id}/campus_users`
- **Method:** GET
- **Returns:** `List[CampusUser]`

## Usage Examples

### Using the Manager (Recommended)

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException

client = Client(
    ...
)

# Get campus users for a specific user
try:
    user = client.users.get_by_login("jdoe")
    campus_users = client.campus_users.get_by_user_id(user.id)
    for cu in campus_users:
        primary_status = "primary" if cu.is_primary else "secondary"
        print(f"Campus ID: {cu.campus_id} ({primary_status})")
except FortyTwoNotFoundException:
    print("User not found")

# Get a specific campus user by ID
campus_user = client.campus_users.get_by_id(campus_user_id=123641)
print(f"User {campus_user.user_id} at campus {campus_user.campus_id}")

# Get all campus users with pagination
campus_users = client.campus_users.get_all(page=1, page_size=100)
```

### Using Resources Directly

```python
from fortytwo.resources.campus_user.resource import (
    GetCampusUsers,
    GetCampusUserById,
    GetCampusUsersByUserId
)

# Get all campus users
campus_users = client.request(GetCampusUsers())

# Get a specific campus user
campus_user = client.request(GetCampusUserById(123641))

# Get campus users for a specific user
campus_users = client.request(GetCampusUsersByUserId(132246))
```

## Data Structure

### Campus User JSON Response
```json
{
  "id": 123641,
  "user_id": 132246,
  "campus_id": 48,
  "is_primary": true,
  "created_at": "2022-08-26T09:32:41.354Z",
  "updated_at": "2022-08-26T09:32:41.354Z"
}
```

## Parameters

For detailed information about filtering, sorting, and ranging campus user queries, see the [Campus User Parameters Documentation](parameter/README.md).

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
    campus_user = client.campus_users.get_by_id(campus_user_id=99999)
    print(f"Found campus user: {campus_user.id}")
except FortyTwoNotFoundException:
    print("Campus user not found")
except FortyTwoUnauthorizedException:
    print("Authentication failed")
except FortyTwoRateLimitException as e:
    print(f"Rate limit exceeded. Wait {e.wait_time} seconds")
except FortyTwoNetworkException:
    print("Network error occurred")
except FortyTwoRequestException as e:
    print(f"Request failed: {e}")
```

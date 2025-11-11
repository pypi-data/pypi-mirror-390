# Cursus User Resource

The Cursus User resource provides access to cursus user data from the 42 API.

## Overview

This module allows you to fetch cursus user information from the 42 API, representing a user's enrollment and progress in a specific cursus. This includes level, grade, and coalition membership.

## Classes

### `CursusUser`
Represents a user's enrollment and progress in a specific cursus.

**Properties:**
- `id` (int): Cursus user's unique identifier
- `begin_at` (datetime): When the user started the cursus
- `end_at` (datetime | None): When the user ended the cursus (None if still active)
- `grade` (str | None): User's grade in the cursus (e.g., "Cadet", "Member")
- `level` (float): User's level in the cursus
- `cursus_id` (int): ID of the cursus
- `has_coalition` (bool): Whether the user has a coalition
- `blackholed_at` (datetime | None): When the user will be blackholed (None if not applicable)
- `created_at` (datetime): When the cursus user entry was created
- `updated_at` (datetime): When the cursus user entry was last updated
- `user` (User): The user enrolled in the cursus
- `cursus` (Cursus): The cursus the user is enrolled in

### Resource Classes

#### `GetCursusUsers`
Fetches all cursus users with optional filtering.
- **Endpoint:** `/cursus_users`
- **Method:** GET
- **Returns:** `List[CursusUser]`

#### `GetCursusUserById`
Fetches a single cursus user by their ID.
- **Endpoint:** `/cursus_users/{id}`
- **Method:** GET
- **Returns:** `CursusUser`

#### `GetCursusUsersByUserId`
Fetches all cursus users for a specific user.
- **Endpoint:** `/users/{user_id}/cursus_users`
- **Method:** GET
- **Returns:** `List[CursusUser]`

#### `GetCursusUsersByCursusId`
Fetches all cursus users for a specific cursus.
- **Endpoint:** `/cursus/{cursus_id}/cursus_users`
- **Method:** GET
- **Returns:** `List[CursusUser]`

## Usage Examples

### Using the Manager (Recommended)

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException

client = Client(
    ...
)

# Get cursus users for a specific user
try:
    user = client.users.get_by_login("jdoe")
    cursus_users = client.cursus_users.get_by_user_id(user.id)
    for cu in cursus_users:
        print(f"Cursus: {cu.cursus.name}")
        print(f"  Level: {cu.level}")
        print(f"  Grade: {cu.grade}")
except FortyTwoNotFoundException:
    print("User not found")

# Get a specific cursus user by ID
cursus_user = client.cursus_users.get_by_id(cursus_user_id=126)
print(f"{cursus_user.user.login} in {cursus_user.cursus.name}: Level {cursus_user.level}")

# Get all cursus users for a specific cursus
cursus_users = client.cursus_users.get_by_cursus_id(cursus_id=21, page=1, page_size=50)
for cu in cursus_users:
    print(f"{cu.user.login}: Level {cu.level}")

# Get all cursus users with pagination
cursus_users = client.cursus_users.get_all(page=1, page_size=100)
```

### Using Resources Directly

```python
from fortytwo.resources.cursus_user.resource import (
    GetCursusUsers,
    GetCursusUserById,
    GetCursusUsersByUserId
)

# Get all cursus users
cursus_users = client.request(GetCursusUsers())

# Get a specific cursus user
cursus_user = client.request(GetCursusUserById(126))

# Get cursus users for a specific user
cursus_users = client.request(GetCursusUsersByUserId(12345))
```

## Data Structure

### Cursus User JSON Response
```json
{
  "id": 126,
  "begin_at": "2016-12-16T07:41:39.516Z",
  "end_at": null,
  "grade": "Cadet",
  "level": 0.0,
  "cursus_id": 2,
  "has_coalition": true,
  "user": {
    "id": 126,
    "login": "darthcae",
    "url": "https://api.intra.42.fr/v2/users/darthcae"
  },
  "cursus": {
    "id": 2,
    "created_at": "2017-11-22T13:41:00.825Z",
    "name": "42",
    "slug": "42"
  }
}
```

## Parameters

For detailed information about filtering, sorting, ranging, and custom parameters for cursus user queries, see the [Cursus User Parameters Documentation](parameter/README.md).

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
    cursus_user = client.cursus_users.get_by_id(cursus_user_id=99999)
    print(f"Found cursus user: {cursus_user.user.login}")
except FortyTwoNotFoundException:
    print("Cursus user not found")
except FortyTwoUnauthorizedException:
    print("Authentication failed")
except FortyTwoRateLimitException as e:
    print(f"Rate limit exceeded. Wait {e.wait_time} seconds")
except FortyTwoNetworkException:
    print("Network error occurred")
except FortyTwoRequestException as e:
    print(f"Request failed: {e}")
```

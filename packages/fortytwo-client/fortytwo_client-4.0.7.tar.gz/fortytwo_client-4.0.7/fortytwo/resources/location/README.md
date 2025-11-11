# Location Resource

The Location resource provides access to 42 School location/session data, tracking where and when users work at campus computers.

## Overview

This module allows you to fetch location information from the 42 API, including session data showing when users log in/out of campus computers, their workstation usage patterns, and time tracking.

## Classes

### `Location`
Represents a location/session record for a user at a campus workstation.

**Properties:**
- `id` (int): Unique location record identifier
- `begin_at` (datetime): Session start time
- `end_at` (Optional[datetime]): Session end time (None if still active)
- `primary` (bool): Whether this is the primary location
- `floor` (Optional[str]): Floor identifier (may be None)
- `row` (Optional[str]): Row identifier (may be None)
- `post` (Optional[str]): Post/seat identifier (may be None)
- `host` (str): Computer/workstation identifier (e.g., "ariel", "e1r1p1")
- `campus_id` (int): Campus identifier where the location is
- `user` (User): User object with basic information (id, login, url)

### Resource Classes

#### `GetLocations`
Fetches all location records.
- **Endpoint:** `/locations`
- **Method:** GET
- **Returns:** `List[Location]`

#### `GetLocationById`
Fetches a specific location by ID.
- **Endpoint:** `/locations/{id}`
- **Method:** GET
- **Returns:** `Location`

#### `GetLocationsByUserId`
Fetches location/session history for a specific user.
- **Endpoint:** `/users/{user_id}/locations`
- **Method:** GET
- **Returns:** `List[Location]`

#### `GetLocationsByCampusId`
Fetches all locations for a specific campus.
- **Endpoint:** `/campus/{campus_id}/locations`
- **Method:** GET
- **Returns:** `List[Location]`

## Usage Examples

### Using the Manager (Recommended)

```python
from fortytwo import Client

client = Client(
    ...
)

# Get all locations with pagination
all_locations = client.locations.get_all(page=1, page_size=100)
print(f"Found {len(all_locations)} location records")

# Get a specific location by ID
location = client.locations.get_by_id(location_id=123456)
print(f"Location: {location.host} at campus {location.campus_id}")
print(f"User: {location.user.login} (ID: {location.user.id})")
print(f"From {location.begin_at} to {location.end_at}")
if location.floor or location.row or location.post:
    print(f"Position: Floor {location.floor}, Row {location.row}, Post {location.post}")

# Get location history for a user
locations = client.locations.get_by_user_id(user_id=12345, page=1, page_size=100)
print(f"Found {len(locations)} location records for user")

# Get all locations for a campus
campus_locations = client.locations.get_by_campus_id(campus_id=1, page=1, page_size=100)
print(f"Found {len(campus_locations)} location records for campus")

# Show current session (if any)
current_session = next((loc for loc in locations if loc.end_at is None), None)
if current_session:
    print(f"Currently logged in at: {current_session.host}")
    print(f"User: {current_session.user.login}")
    print(f"Since: {current_session.begin_at}")

# Show recent sessions
for location in locations[:5]:
    duration = "ongoing" if location.end_at is None else location.end_at - location.begin_at
    print(f"{location.host}: {location.begin_at} -> {duration}")
```

### Using Resources Directly

```python
from fortytwo.resources.location.resource import (
    GetLocations,
    GetLocationById,
    GetLocationsByUserId,
    GetLocationsByCampusId,
)

# Get all locations
all_locations = client.request(GetLocations())

# Get a specific location
location = client.request(GetLocationById(123456))

# Get user location history
locations = client.request(GetLocationsByUserId(12345))

# Get campus locations
campus_locations = client.request(GetLocationsByCampusId(1))
```

## Data Structure

### Location JSON Response
```json
{
  "id": 6,
  "begin_at": "2017-11-22T13:42:10.248Z",
  "end_at": "2017-11-22T13:42:10.248Z",
  "primary": true,
  "floor": null,
  "row": null,
  "post": null,
  "host": "ariel",
  "campus_id": 1,
  "user": {
    "id": 120,
    "login": "obkenobi",
    "url": "https://api.intra.42.fr/v2/users/obkenobi"
  }
}
```

### Active Session (end_at is null)
```json
{
  "id": 123457,
  "begin_at": "2024-03-21T10:15:00Z",
  "end_at": null,
  "primary": true,
  "floor": "1",
  "row": "2",
  "post": "5",
  "host": "e2r3p5",
  "campus_id": 1,
  "user": {
    "id": 12345,
    "login": "jdoe",
    "url": "https://api.intra.42.fr/v2/users/jdoe"
  }
}
```

## Parameters## Parameters

For detailed information about filtering, sorting, and ranging location queries, see the [Location Parameters Documentation](parameter/README.md).

## Error Handling

Methods raise exceptions on errors:

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException, FortyTwoRequestException

client = Client(
    ...
)

try:
    locations = client.locations.get_by_user_id(user_id=99999)
    if not locations:
        print("User has no location history")
    else:
        print(f"Found {len(locations)} location records")
except FortyTwoNotFoundException:
    print("User not found")
except FortyTwoRequestException as e:
    print(f"Request failed: {e}")
```

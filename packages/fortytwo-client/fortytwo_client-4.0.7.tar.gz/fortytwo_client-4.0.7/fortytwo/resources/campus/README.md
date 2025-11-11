# Campus Resource

The Campus resource provides access to 42 School campus information, including location details, contact information, and campus settings.

## Overview

This module allows you to fetch campus data from the 42 API, including campus locations worldwide, their contact details, timezone information, language settings, and operational status.

## Classes

### `Campus`
Represents a 42 School campus with all associated metadata.

**Properties:**
- `id` (int): Unique campus identifier
- `name` (str): Campus name (e.g., "Paris", "Tokyo", "São Paulo")
- `time_zone` (str): Campus timezone (e.g., "Europe/Paris")
- `language` (dict): Campus language information
  - `id` (int): Language identifier
  - `name` (str): Language name (e.g., "Français", "English")
  - `identifier` (str): Language code (e.g., "fr", "en")
- `users_count` (int): Number of users registered at this campus
- `vogsphere_id` (int): Vogsphere system identifier
- `country` (str): Country name
- `address` (str): Street address
- `zip` (str): Postal/ZIP code
- `city` (str): City name
- `website` (str): Campus website URL
- `facebook` (str): Campus Facebook page URL
- `twitter` (str): Campus Twitter/X handle URL
- `active` (bool): Whether the campus is currently active
- `public` (bool): Whether the campus is publicly visible
- `email_extension` (str): Email domain extension (e.g., "42.fr")
- `default_hidden_phone` (bool): Default phone visibility setting

### Resource Classes

#### `GetCampusById`
Fetches a single campus by its ID.
- **Endpoint:** `/campus/{id}`
- **Method:** GET
- **Returns:** `Campus`

#### `GetCampuses`
Fetches all campuses with optional filtering.
- **Endpoint:** `/campus`
- **Method:** GET
- **Returns:** `List[Campus]`

## Usage Examples

### Using the Manager (Recommended)

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException

client = Client(
    ...
)

# Get a specific campus
try:
    campus = client.campuses.get_by_id(campus_id=1)
    print(f"Campus: {campus.name}")
    print(f"Location: {campus.city}, {campus.country}")
    print(f"Timezone: {campus.time_zone}")
    print(f"Users: {campus.users_count}")
except FortyTwoNotFoundException:
    print("Campus not found")

# Get all campuses with pagination
campuses = client.campuses.get_all(page=1, page_size=50)
for campus in campuses:
    print(f"{campus.id}: {campus.name} ({campus.city}, {campus.country})")

# Get only active campuses
from fortytwo.resources.campus import CampusParameters

active_campuses = client.campuses.get_all(
    CampusParameters.Filter.by_active(True),
    page=1,
    page_size=100
)
```

### Using Resources Directly

```python
from fortytwo.resources.campus.resource import GetCampusById, GetCampuses

# Get a specific campus
campus = client.request(GetCampusById(1))

# Get all campuses
campuses = client.request(GetCampuses())
```

## Data Structure

### Campus JSON Response
```json
{
  "id": 1,
  "name": "Paris",
  "time_zone": "Europe/Paris",
  "language": {
    "id": 1,
    "name": "Français",
    "identifier": "fr"
  },
  "users_count": 22997,
  "vogsphere_id": 1,
  "country": "France",
  "address": "96, boulevard Bessières",
  "zip": "75017",
  "city": "Paris",
  "website": "http://www.42.fr/",
  "facebook": "https://facebook.com/42born2code",
  "twitter": "https://twitter.com/42born2code",
  "active": true,
  "public": true,
  "email_extension": "42.fr",
  "default_hidden_phone": false
}
```

## Parameters

For detailed information about filtering, sorting, and ranging campus queries, see the [Campus Parameters Documentation](parameter/README.md).

## Error Handling

Methods raise exceptions on errors:

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException, FortyTwoRequestException

client = Client(
    ...
)

try:
    campus = client.campuses.get_by_id(999999)
except FortyTwoNotFoundException:
    print("Campus not found")
except FortyTwoRequestException as e:
    print(f"API error: {e}")
```

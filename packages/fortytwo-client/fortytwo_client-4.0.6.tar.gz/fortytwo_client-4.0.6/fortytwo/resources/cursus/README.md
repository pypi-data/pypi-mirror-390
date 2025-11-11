# Cursus Resource

The Cursus resource provides access to 42 School cursus (curriculum) information.

## Overview

This module allows you to fetch cursus data from the 42 API, including different educational tracks offered at 42 Schools worldwide.

## Classes

### `Cursus`
Represents a 42 School cursus with all associated metadata.

**Properties:**
- `id` (int): Unique cursus identifier
- `created_at` (str): ISO 8601 timestamp of when the cursus was created
- `name` (str): Cursus name (e.g., "42", "42cursus", "Piscine C")
- `slug` (str): URL-friendly version of the cursus name
- `kind` (str): Type of cursus

### Resource Classes

#### `GetCursusById`
Fetches a single cursus by its ID.
- **Endpoint:** `/cursus/{id}`
- **Method:** GET
- **Returns:** `Cursus`

#### `GetCursuses`
Fetches all cursuses with optional filtering.
- **Endpoint:** `/cursus`
- **Method:** GET
- **Returns:** `List[Cursus]`

## Usage Examples

### Using the Manager (Recommended)

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException

client = Client(
    ...
)

# Get a specific cursus
try:
    cursus = client.cursuses.get_by_id(cursus_id=2)
    print(f"Cursus: {cursus.name}")
    print(f"Slug: {cursus.slug}")
    print(f"Created: {cursus.created_at}")
except FortyTwoNotFoundException:
    print("Cursus not found")

# Get all cursuses with pagination
cursuses = client.cursuses.get_all(page=1, page_size=50)
for cursus in cursuses:
    print(f"{cursus.id}: {cursus.name}")

# Get cursuses with filtering
from fortytwo.resources.cursus import CursusParameters

cursuses = client.cursuses.get_all(
    CursusParameters.Filter.by_name("42"),
    page=1,
    page_size=100
)
```

### Using Resources Directly

```python
from fortytwo.resources.cursus.resource import GetCursusById, GetCursuses

# Get a specific cursus
cursus = client.request(GetCursusById(2))

# Get all cursuses
cursuses = client.request(GetCursuses())
```

## Data Structure

### Cursus JSON Response
```json
{
  "id": 2,
  "created_at": "2017-11-22T13:41:00.825Z",
  "name": "42",
  "slug": "42",
  "kind": "main"
}
```

## Parameters

For detailed information about filtering, sorting, and ranging cursus queries, see the [Cursus Parameters Documentation](parameter/README.md).

## Error Handling

Methods raise exceptions on errors:

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException, FortyTwoRequestException

client = Client(
    ...
)

try:
    cursus = client.cursuses.get_by_id(999999)
except FortyTwoNotFoundException:
    print("Cursus not found")
except FortyTwoRequestException as e:
    print(f"API error: {e}")
```

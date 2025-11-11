# Cursus Parameters

This module provides filtering, sorting, and ranging capabilities for cursus queries.

## Overview

The Cursus Parameters module allows you to:
- **Filter** cursuses by specific field values
- **Sort** cursuses by any field in ascending or descending order
- **Range** cursuses by numeric or date field boundaries

## Usage

```python
from fortytwo import Client
from fortytwo.resources.cursus import CursusParameters
from fortytwo.request.parameter.parameter import SortDirection

client = Client(
    ...
)

# Filter by name
cursuses = client.cursuses.get_all(
    CursusParameters.Filter.by_name("42")
)

# Sort by name
cursuses = client.cursuses.get_all(
    CursusParameters.Sort.by_name(SortDirection.ASCENDING)
)

# Range by ID
cursuses = client.cursuses.get_all(
    CursusParameters.Range.by_id(min_id=1, max_id=50)
)

# Combine multiple parameters
cursuses = client.cursuses.get_all(
    CursusParameters.Filter.by_kind("main"),
    CursusParameters.Sort.by_created_at(SortDirection.DESCENDING),
    CursusParameters.Range.by_id(min_id=1, max_id=100)
)
```

---

## Filter Parameters

Filter cursuses by specific field values.

### `by_id(cursus_id: Union[str, int])`
Filter by cursus ID.

**Args:**
- `cursus_id` (Union[str, int]): The cursus ID

**Example:**
```python
cursus = client.cursuses.get_all(
    CursusParameters.Filter.by_id(2)
)
```

### `by_name(name: str)`
Filter by cursus name.

**Args:**
- `name` (str): The cursus name

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Filter.by_name("42")
)
```

### `by_created_at(created_at: Union[str, datetime])`
Filter by cursus creation date.

**Args:**
- `created_at` (Union[str, datetime]): The creation date (ISO 8601 format string or datetime object)

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Filter.by_created_at("2017-11-22T13:41:00.825Z")
)
```

### `by_updated_at(updated_at: Union[str, datetime])`
Filter by cursus last update date.

**Args:**
- `updated_at` (Union[str, datetime]): The update date (ISO 8601 format string or datetime object)

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Filter.by_updated_at("2023-01-01T00:00:00.000Z")
)
```

### `by_slug(slug: str)`
Filter by cursus slug.

**Args:**
- `slug` (str): The cursus slug

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Filter.by_slug("42")
)
```

### `by_kind(kind: str)`
Filter by cursus kind.

**Args:**
- `kind` (str): The cursus kind

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Filter.by_kind("main")
)
```

### `by_restricted(restricted: bool)`
Filter by restricted status.

**Args:**
- `restricted` (bool): The restricted status

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Filter.by_restricted(False)
)
```

### `by_is_subscriptable(is_subscriptable: bool)`
Filter by subscriptable status.

**Args:**
- `is_subscriptable` (bool): The subscriptable status

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Filter.by_is_subscriptable(True)
)
```

---

## Sort Parameters

Sort cursus results by various fields.

> **Note**: All sort methods use the `SortDirection` enum to specify ascending or descending order. Import it with:
> ```python
> from fortytwo.request.parameter.parameter import SortDirection
> ```

### `by_id`

Sort cursuses by ID.

**Parameters:**
- `direction` (SortDirection, optional): Sort direction. Default is `SortDirection.ASCENDING`.

**Usage:**
```python
from fortytwo.resources.cursus import CursusParameters
from fortytwo.request.parameter.parameter import SortDirection

# Sort by ID ascending (default)
params = CursusParameters.Sort.by_id()

# Sort by ID descending
params = CursusParameters.Sort.by_id(SortDirection.DESCENDING)
```

### `by_name`

Sort cursuses by name.

**Parameters:**
- `direction` (SortDirection, optional): Sort direction. Default is `SortDirection.ASCENDING`.

**Usage:**
```python
from fortytwo.resources.cursus import CursusParameters
from fortytwo.request.parameter.parameter import SortDirection

# Sort by name ascending (default)
params = CursusParameters.Sort.by_name()

# Sort by name descending
params = CursusParameters.Sort.by_name(SortDirection.DESCENDING)
```

### `by_created_at`

Sort cursuses by creation date.

**Parameters:**
- `direction` (SortDirection, optional): Sort direction. Default is `SortDirection.ASCENDING`.

**Usage:**
```python
from fortytwo.resources.cursus import CursusParameters
from fortytwo.request.parameter.parameter import SortDirection

# Sort by creation date ascending (default)
params = CursusParameters.Sort.by_created_at()

# Sort by creation date descending
params = CursusParameters.Sort.by_created_at(SortDirection.DESCENDING)
```

### `by_updated_at`

Sort cursuses by last update date.

**Parameters:**
- `direction` (SortDirection, optional): Sort direction. Default is `SortDirection.ASCENDING`.

**Usage:**
```python
from fortytwo.resources.cursus import CursusParameters
from fortytwo.request.parameter.parameter import SortDirection

# Sort by update date ascending (default)
params = CursusParameters.Sort.by_updated_at()

# Sort by update date descending
params = CursusParameters.Sort.by_updated_at(SortDirection.DESCENDING)
```

### `by_slug`

Sort cursuses by slug.

**Parameters:**
- `direction` (SortDirection, optional): Sort direction. Default is `SortDirection.ASCENDING`.

**Usage:**
```python
from fortytwo.resources.cursus import CursusParameters
from fortytwo.request.parameter.parameter import SortDirection

# Sort by slug ascending (default)
params = CursusParameters.Sort.by_slug()

# Sort by slug descending
params = CursusParameters.Sort.by_slug(SortDirection.DESCENDING)
```

### `by_kind`

Sort cursuses by kind.

**Parameters:**
- `direction` (SortDirection, optional): Sort direction. Default is `SortDirection.ASCENDING`.

**Usage:**
```python
from fortytwo.resources.cursus import CursusParameters
from fortytwo.request.parameter.parameter import SortDirection

# Sort by kind ascending (default)
params = CursusParameters.Sort.by_kind()

# Sort by kind descending
params = CursusParameters.Sort.by_kind(SortDirection.DESCENDING)
```

### `by_restricted`

Sort cursuses by restricted status.

**Parameters:**
- `direction` (SortDirection, optional): Sort direction. Default is `SortDirection.ASCENDING`.

**Usage:**
```python
from fortytwo.resources.cursus import CursusParameters
from fortytwo.request.parameter.parameter import SortDirection

# Sort by restricted ascending (default)
params = CursusParameters.Sort.by_restricted()

# Sort by restricted descending
params = CursusParameters.Sort.by_restricted(SortDirection.DESCENDING)
```

### `by_is_subscriptable`

Sort cursuses by subscriptable status.

**Parameters:**
- `direction` (SortDirection, optional): Sort direction. Default is `SortDirection.ASCENDING`.

**Usage:**
```python
from fortytwo.resources.cursus import CursusParameters
from fortytwo.request.parameter.parameter import SortDirection

# Sort by is_subscriptable ascending (default)
params = CursusParameters.Sort.by_is_subscriptable()

# Sort by is_subscriptable descending
params = CursusParameters.Sort.by_is_subscriptable(SortDirection.DESCENDING)
```

---

## Range Parameters

Filter cursuses by field value ranges (min to max, inclusive).

### `by_id(min_id: Union[str, int], max_id: Union[str, int])`
Filter by ID range.

**Args:**
- `min_id` (Union[str, int]): Minimum ID (inclusive)
- `max_id` (Union[str, int]): Maximum ID (inclusive)

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Range.by_id(min_id=1, max_id=10)
)
```

### `by_name(min_name: str, max_name: str)`
Filter by name range.

**Args:**
- `min_name` (str): Minimum name (inclusive)
- `max_name` (str): Maximum name (inclusive)

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Range.by_name(min_name="A", max_name="M")
)
```

### `by_created_at(min_created_at: Union[str, datetime], max_created_at: Union[str, datetime])`
Filter by creation date range.

**Args:**
- `min_created_at` (Union[str, datetime]): Minimum creation date (inclusive)
- `max_created_at` (Union[str, datetime]): Maximum creation date (inclusive)

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Range.by_created_at(
        min_created_at="2017-01-01T00:00:00.000Z",
        max_created_at="2017-12-31T23:59:59.999Z"
    )
)
```

### `by_updated_at(min_updated_at: Union[str, datetime], max_updated_at: Union[str, datetime])`
Filter by update date range.

**Args:**
- `min_updated_at` (Union[str, datetime]): Minimum update date (inclusive)
- `max_updated_at` (Union[str, datetime]): Maximum update date (inclusive)

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Range.by_updated_at(
        min_updated_at="2023-01-01T00:00:00.000Z",
        max_updated_at="2023-12-31T23:59:59.999Z"
    )
)
```

### `by_slug(min_slug: str, max_slug: str)`
Filter by slug range.

**Args:**
- `min_slug` (str): Minimum slug (inclusive)
- `max_slug` (str): Maximum slug (inclusive)

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Range.by_slug(min_slug="a", max_slug="m")
)
```

### `by_kind(min_kind: str, max_kind: str)`
Filter by kind range.

**Args:**
- `min_kind` (str): Minimum kind (inclusive)
- `max_kind` (str): Maximum kind (inclusive)

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Range.by_kind(min_kind="a", max_kind="z")
)
```

### `by_restricted(min_restricted: bool, max_restricted: bool)`
Filter by restricted status range.

**Args:**
- `min_restricted` (bool): Minimum restricted value (inclusive)
- `max_restricted` (bool): Maximum restricted value (inclusive)

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Range.by_restricted(min_restricted=False, max_restricted=True)
)
```

### `by_is_subscriptable(min_is_subscriptable: bool, max_is_subscriptable: bool)`
Filter by subscriptable status range.

**Args:**
- `min_is_subscriptable` (bool): Minimum subscriptable value (inclusive)
- `max_is_subscriptable` (bool): Maximum subscriptable value (inclusive)

**Example:**
```python
cursuses = client.cursuses.get_all(
    CursusParameters.Range.by_is_subscriptable(min_is_subscriptable=False, max_is_subscriptable=True)
)
```

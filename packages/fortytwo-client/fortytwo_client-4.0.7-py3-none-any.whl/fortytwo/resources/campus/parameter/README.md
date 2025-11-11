# Campus Parameters

This module provides filtering, sorting, and ranging capabilities for campus queries.

## Overview

The Campus Parameters module allows you to:
- **Filter** campuses by specific field values
- **Sort** campuses by any field in ascending or descending order
- **Range** campuses by numeric or date field boundaries

## Usage

```python
from fortytwo import Client
from fortytwo.resources.campus import CampusParameters
from fortytwo.request.parameter.parameter import SortDirection

client = Client(
    ...
)

# Filter by country
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_country("France")
)

# Sort by name
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_name(SortDirection.ASCENDING)
)

# Range by ID
campuses = client.campuses.get_all(
    CampusParameters.Range.by_id(min=1, max=50)
)

# Combine multiple parameters
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_active(True),
    CampusParameters.Filter.by_country("United States"),
    CampusParameters.Sort.by_users_count(SortDirection.DESCENDING),
    CampusParameters.Range.by_id(min=1, max=100)
)
```

---

## Filter Parameters

Filter campuses by specific field values.

### `by_id(campus_id: int)`
Filter by campus ID.

**Args:**
- `campus_id` (int): The campus ID

**Example:**
```python
campus = client.campuses.get_all(
    CampusParameters.Filter.by_id(1)
)
```

### `by_name(name: str)`
Filter by campus name.

**Args:**
- `name` (str): The campus name

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_name("Paris")
)
```

### `by_created_at(created_at: str)`
Filter by campus creation date.

**Args:**
- `created_at` (str): The creation date (ISO 8601 format)

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_created_at("2022-01-01T00:00:00.000Z")
)
```

### `by_updated_at(updated_at: str)`
Filter by campus last update date.

**Args:**
- `updated_at` (str): The update date (ISO 8601 format)

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_updated_at("2023-01-01T00:00:00.000Z")
)
```

### `by_time_zone(time_zone: str)`
Filter by campus timezone.

**Args:**
- `time_zone` (str): The timezone (e.g., "Europe/Paris")

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_time_zone("America/Los_Angeles")
)
```

### `by_language_id(language_id: int)`
Filter by language ID.

**Args:**
- `language_id` (int): The language ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_language_id(1)  # French
)
```

### `by_slug(slug: str)`
Filter by campus slug.

**Args:**
- `slug` (str): The campus slug

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_slug("paris")
)
```

### `by_users_count(users_count: int)`
Filter by number of users.

**Args:**
- `users_count` (int): The number of users

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_users_count(1000)
)
```

### `by_vogsphere_id(vogsphere_id: int)`
Filter by Vogsphere ID.

**Args:**
- `vogsphere_id` (int): The Vogsphere ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_vogsphere_id(1)
)
```

### `by_country(country: str)`
Filter by country name.

**Args:**
- `country` (str): The country name

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_country("France")
)
```

### `by_address(address: str)`
Filter by street address.

**Args:**
- `address` (str): The street address

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_address("96, boulevard Bessières")
)
```

### `by_zip(zip_code: str)`
Filter by postal/ZIP code.

**Args:**
- `zip_code` (str): The ZIP code

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_zip("75017")
)
```

### `by_city(city: str)`
Filter by city name.

**Args:**
- `city` (str): The city name

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_city("Paris")
)
```

### `by_website(website: str)`
Filter by campus website URL.

**Args:**
- `website` (str): The website URL

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_website("http://www.42.fr/")
)
```

### `by_facebook(facebook: str)`
Filter by Facebook page URL.

**Args:**
- `facebook` (str): The Facebook URL

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_facebook("https://facebook.com/42born2code")
)
```

### `by_twitter(twitter: str)`
Filter by Twitter/X handle URL.

**Args:**
- `twitter` (str): The Twitter URL

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_twitter("https://twitter.com/42born2code")
)
```

### `by_active(active: bool)`
Filter by campus active status.

**Args:**
- `active` (bool): True for active campuses, False for inactive

**Example:**
```python
# Get only active campuses
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_active(True)
)
```

### `by_public(public: bool)`
Filter by campus public visibility.

**Args:**
- `public` (bool): True for public campuses, False for private

**Example:**
```python
# Get only public campuses
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_public(True)
)
```

### `by_email_extension(email_extension: str)`
Filter by email domain extension.

**Args:**
- `email_extension` (str): The email extension (e.g., "42.fr")

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_email_extension("42.fr")
)
```

### `by_default_hidden_phone(default_hidden_phone: bool)`
Filter by default phone visibility setting.

**Args:**
- `default_hidden_phone` (bool): The default phone visibility

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_default_hidden_phone(False)
)
```

### `by_endpoint_id(endpoint_id: int)`
Filter by endpoint ID.

**Args:**
- `endpoint_id` (int): The endpoint ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_endpoint_id(1)
)
```

### `by_endpoint_snapshot_id(endpoint_snapshot_id: int)`
Filter by endpoint snapshot ID.

**Args:**
- `endpoint_snapshot_id` (int): The endpoint snapshot ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_endpoint_snapshot_id(1)
)
```

### `by_logo_url(logo_url: str)`
Filter by logo URL.

**Args:**
- `logo_url` (str): The logo URL

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_logo_url("https://example.com/logo.png")
)
```

### `by_logo_image(logo_image: str)`
Filter by logo image.

**Args:**
- `logo_image` (str): The logo image

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_logo_image("logo.png")
)
```

### `by_company_id(company_id: int)`
Filter by company ID.

**Args:**
- `company_id` (int): The company ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_company_id(1)
)
```

### `by_primary_campus_of_id(primary_campus_of_id: int)`
Filter by primary campus ID.

**Args:**
- `primary_campus_of_id` (int): The primary campus ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_primary_campus_of_id(1)
)
```

### `by_pricing_id(pricing_id: int)`
Filter by pricing ID.

**Args:**
- `pricing_id` (int): The pricing ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_pricing_id(1)
)
```

### `by_parent_id(parent_id: int)`
Filter by parent campus ID.

**Args:**
- `parent_id` (int): The parent campus ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_parent_id(1)
)
```

### `by_main_campus(main_campus: bool)`
Filter by main campus status.

**Args:**
- `main_campus` (bool): True for main campuses, False otherwise

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_main_campus(True)
)
```

### `by_campuses_cities_id(campuses_cities_id: int)`
Filter by campus city ID.

**Args:**
- `campuses_cities_id` (int): The campus city ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_campuses_cities_id(1)
)
```

### `by_timezone_utc_hour_offset(timezone_utc_hour_offset: int)`
Filter by UTC hour offset.

**Args:**
- `timezone_utc_hour_offset` (int): The UTC hour offset

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_timezone_utc_hour_offset(2)
)
```

### `by_language_name(language_name: str)`
Filter by language name.

**Args:**
- `language_name` (str): The language name

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_language_name("English")
)
```

### `by_language_identifier(language_identifier: str)`
Filter by language identifier.

**Args:**
- `language_identifier` (str): The language identifier (e.g., "en", "fr")

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_language_identifier("en")
)
```

### `by_language_created_at(language_created_at: str)`
Filter by language creation date.

**Args:**
- `language_created_at` (str): The language creation date (ISO 8601 format)

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_language_created_at("2022-01-01T00:00:00.000Z")
)
```

### `by_language_updated_at(language_updated_at: str)`
Filter by language update date.

**Args:**
- `language_updated_at` (str): The language update date (ISO 8601 format)

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Filter.by_language_updated_at("2023-01-01T00:00:00.000Z")
)
```

---

## Sort Parameters

Sort campuses by field values in ascending or descending order. Use the `SortDirection` enum to specify the sort order.

**Import the SortDirection enum:**
```python
from fortytwo.request.parameter.parameter import SortDirection
```

### `by_id(direction: SortDirection = SortDirection.DESCENDING)`
Sort by campus ID.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.DESCENDING.

**Example:**
```python
# Sort by ID descending (default)
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_id()
)

# Sort by ID ascending
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_id(SortDirection.ASCENDING)
)
```

### `by_name(direction: SortDirection = SortDirection.ASCENDING)`
Sort by campus name.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_name(SortDirection.ASCENDING)
)
```

### `by_created_at(direction: SortDirection = SortDirection.DESCENDING)`
Sort by campus creation date.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.DESCENDING.

**Example:**
```python
# Get newest campuses first
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_created_at(SortDirection.DESCENDING)
)
```

### `by_updated_at(direction: SortDirection = SortDirection.DESCENDING)`
Sort by campus last update date.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.DESCENDING.

**Example:**
```python
# Get recently updated campuses
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_updated_at(SortDirection.DESCENDING)
)
```

### `by_time_zone(direction: SortDirection = SortDirection.ASCENDING)`
Sort by campus timezone.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_time_zone(SortDirection.ASCENDING)
)
```

### `by_language_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by language ID.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_language_id(SortDirection.ASCENDING)
)
```

### `by_users_count(direction: SortDirection = SortDirection.ASCENDING)`
Sort by number of users.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
# Get campuses with most users first
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_users_count(SortDirection.DESCENDING)
)
```

### `by_vogsphere_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by Vogsphere ID.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_vogsphere_id(SortDirection.ASCENDING)
)
```

### `by_country(direction: SortDirection = SortDirection.ASCENDING)`
Sort by country name.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_country(SortDirection.ASCENDING)
)
```

### `by_city(direction: SortDirection = SortDirection.ASCENDING)`
Sort by city name.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_city(SortDirection.ASCENDING)
)
```

### `by_zip(direction: SortDirection = SortDirection.ASCENDING)`
Sort by postal/ZIP code.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_zip(SortDirection.ASCENDING)
)
```

### `by_slug(direction: SortDirection = SortDirection.ASCENDING)`
Sort by campus slug.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_slug(SortDirection.ASCENDING)
)
```

### `by_address(direction: SortDirection = SortDirection.ASCENDING)`
Sort by street address.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_address(SortDirection.ASCENDING)
)
```

### `by_website(direction: SortDirection = SortDirection.ASCENDING)`
Sort by website URL.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_website(SortDirection.ASCENDING)
)
```

### `by_facebook(direction: SortDirection = SortDirection.ASCENDING)`
Sort by Facebook URL.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_facebook(SortDirection.ASCENDING)
)
```

### `by_twitter(direction: SortDirection = SortDirection.ASCENDING)`
Sort by Twitter URL.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_twitter(SortDirection.ASCENDING)
)
```

### `by_active(direction: SortDirection = SortDirection.DESCENDING)`
Sort by active status.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.DESCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_active(SortDirection.DESCENDING)
)
```

### `by_public(direction: SortDirection = SortDirection.DESCENDING)`
Sort by public visibility.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.DESCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_public(SortDirection.DESCENDING)
)
```

### `by_email_extension(direction: SortDirection = SortDirection.ASCENDING)`
Sort by email extension.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_email_extension(SortDirection.ASCENDING)
)
```

### `by_default_hidden_phone(direction: SortDirection = SortDirection.DESCENDING)`
Sort by phone visibility.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.DESCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_default_hidden_phone(SortDirection.ASCENDING)
)
```

### `by_endpoint_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by endpoint ID.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_endpoint_id(SortDirection.ASCENDING)
)
```

### `by_endpoint_snapshot_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by endpoint snapshot ID.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_endpoint_snapshot_id(SortDirection.ASCENDING)
)
```

### `by_logo_url(direction: SortDirection = SortDirection.ASCENDING)`
Sort by logo URL.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_logo_url(SortDirection.ASCENDING)
)
```

### `by_logo_image(direction: SortDirection = SortDirection.ASCENDING)`
Sort by logo image.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_logo_image(SortDirection.ASCENDING)
)
```

### `by_company_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by company ID.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_company_id(SortDirection.ASCENDING)
)
```

### `by_primary_campus_of_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by primary campus ID.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_primary_campus_of_id(SortDirection.ASCENDING)
)
```

### `by_pricing_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by pricing ID.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_pricing_id(SortDirection.ASCENDING)
)
```

### `by_parent_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by parent campus ID.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_parent_id(SortDirection.ASCENDING)
)
```

### `by_main_campus(direction: SortDirection = SortDirection.ASCENDING)`
Sort by main campus status.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Sort.by_main_campus(SortDirection.DESCENDING)
)
```

### `by_campuses_cities_id(direction: SortDirection = SortDirection.ASCENDING)`
Sort by campus city ID.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

campuses = client.campuses.get_all(
    CampusParameters.Sort.by_campuses_cities_id(SortDirection.ASCENDING)
)
```

### `by_timezone_utc_hour_offset(direction: SortDirection = SortDirection.ASCENDING)`
Sort by UTC hour offset.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

campuses = client.campuses.get_all(
    CampusParameters.Sort.by_timezone_utc_hour_offset(SortDirection.ASCENDING)
)
```

### `by_language_name(direction: SortDirection = SortDirection.ASCENDING)`
Sort by language name.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

campuses = client.campuses.get_all(
    CampusParameters.Sort.by_language_name(SortDirection.ASCENDING)
)
```

### `by_language_identifier(direction: SortDirection = SortDirection.ASCENDING)`
Sort by language identifier.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

campuses = client.campuses.get_all(
    CampusParameters.Sort.by_language_identifier(SortDirection.ASCENDING)
)
```

### `by_language_created_at(direction: SortDirection = SortDirection.ASCENDING)`
Sort by language creation date.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

campuses = client.campuses.get_all(
    CampusParameters.Sort.by_language_created_at(SortDirection.DESCENDING)
)
```

### `by_language_updated_at(direction: SortDirection = SortDirection.ASCENDING)`
Sort by language update date.

**Args:**
- `direction` (SortDirection): Sort direction. Defaults to SortDirection.ASCENDING.

**Example:**
```python
from fortytwo.request.parameter.parameter import SortDirection

campuses = client.campuses.get_all(
    CampusParameters.Sort.by_language_updated_at(SortDirection.DESCENDING)
)
```

---

## Range Parameters

Filter campuses by numeric or date field ranges.

### `by_id(min: int | None = None, max: int | None = None)`
Filter by campus ID range.

**Args:**
- `min` (int | None, optional): Minimum campus ID
- `max` (int | None, optional): Maximum campus ID

**Example:**
```python
# Get campuses with IDs between 1 and 50
campuses = client.campuses.get_all(
    CampusParameters.Range.by_id(min=1, max=50)
)

# Get campuses with ID >= 10
campuses = client.campuses.get_all(
    CampusParameters.Range.by_id(min=10)
)

# Get campuses with ID <= 100
campuses = client.campuses.get_all(
    CampusParameters.Range.by_id(max=100)
)
```

### `by_created_at(min: str | None = None, max: str | None = None)`
Filter by campus creation date range.

**Args:**
- `min` (str | None, optional): Minimum creation date (ISO 8601 format)
- `max` (str | None, optional): Maximum creation date (ISO 8601 format)

**Example:**
```python
# Get campuses created in 2022
campuses = client.campuses.get_all(
    CampusParameters.Range.by_created_at(
        min="2022-01-01T00:00:00.000Z",
        max="2022-12-31T23:59:59.999Z"
    )
)
```

### `by_updated_at(min: str | None = None, max: str | None = None)`
Filter by campus last update date range.

**Args:**
- `min` (str | None, optional): Minimum update date (ISO 8601 format)
- `max` (str | None, optional): Maximum update date (ISO 8601 format)

**Example:**
```python
# Get campuses updated since 2023
campuses = client.campuses.get_all(
    CampusParameters.Range.by_updated_at(min="2023-01-01T00:00:00.000Z")
)
```

### `by_language_id(min: int | None = None, max: int | None = None)`
Filter by language ID range.

**Args:**
- `min` (int | None, optional): Minimum language ID
- `max` (int | None, optional): Maximum language ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Range.by_language_id(min=1, max=5)
)
```

### `by_users_count(min: int | None = None, max: int | None = None)`
Filter by number of users range.

**Args:**
- `min` (int | None, optional): Minimum number of users
- `max` (int | None, optional): Maximum number of users

**Example:**
```python
# Get large campuses (>1000 users)
campuses = client.campuses.get_all(
    CampusParameters.Range.by_users_count(min=1000)
)

# Get medium-sized campuses (100-1000 users)
campuses = client.campuses.get_all(
    CampusParameters.Range.by_users_count(min=100, max=1000)
)
```

### `by_vogsphere_id(min: int | None = None, max: int | None = None)`
Filter by Vogsphere ID range.

**Args:**
- `min` (int | None, optional): Minimum Vogsphere ID
- `max` (int | None, optional): Maximum Vogsphere ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Range.by_vogsphere_id(min=1, max=10)
)
```

### `by_endpoint_id(min: int | None = None, max: int | None = None)`
Filter by endpoint ID range.

**Args:**
- `min` (int | None, optional): Minimum endpoint ID
- `max` (int | None, optional): Maximum endpoint ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Range.by_endpoint_id(min=1, max=100)
)
```

### `by_endpoint_snapshot_id(min: int | None = None, max: int | None = None)`
Filter by endpoint snapshot ID range.

**Args:**
- `min` (int | None, optional): Minimum endpoint snapshot ID
- `max` (int | None, optional): Maximum endpoint snapshot ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Range.by_endpoint_snapshot_id(min=1, max=100)
)
```

### `by_company_id(min: int | None = None, max: int | None = None)`
Filter by company ID range.

**Args:**
- `min` (int | None, optional): Minimum company ID
- `max` (int | None, optional): Maximum company ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Range.by_company_id(min=1, max=50)
)
```

### `by_primary_campus_of_id(min: int | None = None, max: int | None = None)`
Filter by primary campus ID range.

**Args:**
- `min` (int | None, optional): Minimum primary campus ID
- `max` (int | None, optional): Maximum primary campus ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Range.by_primary_campus_of_id(min=1, max=50)
)
```

### `by_pricing_id(min: int | None = None, max: int | None = None)`
Filter by pricing ID range.

**Args:**
- `min` (int | None, optional): Minimum pricing ID
- `max` (int | None, optional): Maximum pricing ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Range.by_pricing_id(min=1, max=10)
)
```

### `by_parent_id(min: int | None = None, max: int | None = None)`
Filter by parent campus ID range.

**Args:**
- `min` (int | None, optional): Minimum parent campus ID
- `max` (int | None, optional): Maximum parent campus ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Range.by_parent_id(min=1, max=50)
)
```

### `by_campuses_cities_id(min: int | None = None, max: int | None = None)`
Filter by campus city ID range.

**Args:**
- `min` (int | None, optional): Minimum campus city ID
- `max` (int | None, optional): Maximum campus city ID

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Range.by_campuses_cities_id(min=1, max=100)
)
```

### `by_timezone_utc_hour_offset(min: int | None = None, max: int | None = None)`
Filter by UTC hour offset range.

**Args:**
- `min` (int | None, optional): Minimum UTC hour offset
- `max` (int | None, optional): Maximum UTC hour offset

**Example:**
```python
# Get campuses in UTC-8 to UTC+2 timezone range
campuses = client.campuses.get_all(
    CampusParameters.Range.by_timezone_utc_hour_offset(min=-8, max=2)
)
```

### `by_language_created_at(min: str | None = None, max: str | None = None)`
Filter by language creation date range.

**Args:**
- `min` (str | None, optional): Minimum language creation date (ISO 8601 format)
- `max` (str | None, optional): Maximum language creation date (ISO 8601 format)

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Range.by_language_created_at(
        min="2020-01-01T00:00:00.000Z",
        max="2023-12-31T23:59:59.999Z"
    )
)
```

### `by_language_updated_at(min: str | None = None, max: str | None = None)`
Filter by language update date range.

**Args:**
- `min` (str | None, optional): Minimum language update date (ISO 8601 format)
- `max` (str | None, optional): Maximum language update date (ISO 8601 format)

**Example:**
```python
campuses = client.campuses.get_all(
    CampusParameters.Range.by_language_updated_at(min="2023-01-01T00:00:00.000Z")
)
```

---

## Examples

See the [`example/`](../../../../example/) directory for complete working examples.

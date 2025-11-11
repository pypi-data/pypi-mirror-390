# User Resource

The User resource provides access to 42 School user data and operations.

## Overview

This module allows you to fetch user information from the 42 API, including basic profile data, authentication status, images, and more.

## Classes

### `UserImage`
Represents a user's profile image with different versions.

**Properties:**
- `link` (str): Direct link to the profile image
- `large` (str): URL to large version of the image
- `medium` (str): URL to medium version of the image
- `small` (str): URL to small version of the image
- `micro` (str): URL to micro version of the image

**Methods:**
- `to_dict()`: Convert to dictionary format matching API response

**Example:**
```python
user = client.users.get_by_id(user_id=12345)
print(user.image.link)       # Direct link
print(user.image.large)      # Large version URL
print(user.image.medium)     # Medium version URL
print(user.image.small)      # Small version URL
print(user.image.micro)      # Micro version URL
```

### `User`
Represents a 42 School user with all their associated data.

**Properties:**
- `id` (int): Unique user identifier
- `email` (str): User's email address
- `login` (str): User's login name
- `first_name` (str): User's first name
- `last_name` (str): User's last name
- `usual_full_name` (str): User's display name
- `usual_first_name` (str | None): User's usual first name (may be None)
- `url` (str): API URL for the user
- `phone` (str): User's phone number
- `displayname` (str): User's display name
- `kind` (str): User type/kind (e.g., "student", "staff")
- `image` (UserImage): Profile images with link and versions (large, medium, small, micro)
- `staff` (bool): Whether the user is staff
- `correction_point` (int): Number of correction points
- `pool_month` (str): Pool month (e.g., "september")
- `pool_year` (str): Pool year (e.g., "2022")
- `location` (str | None): Current location (None if not logged in)
- `wallet` (int): Wallet balance
- `anonymize_date` (datetime): Date when user data will be anonymized
- `data_erasure_date` (datetime): Date when user data will be erased
- `created_at` (datetime): Account creation date
- `updated_at` (datetime): Last profile update date
- `alumnized_at` (datetime | None): Date when user became alumni (None if not alumni)
- `alumni` (bool): Whether the user is an alumnus
- `active` (bool): Whether the user account is active
- `cursus_users` (list): List of cursus user enrollments
- `projects_users` (list): List of project completions
- `campus` (list): List of associated campuses
- `campus_users` (list): List of campus user associations

### Resource Classes

#### `GetUserById`
Fetches a single user by their ID.
- **Endpoint:** `/users/{id}`
- **Method:** GET
- **Returns:** `User`

#### `GetUsers`
Fetches all users with optional filtering.
- **Endpoint:** `/users`
- **Method:** GET
- **Returns:** `List[User]`

## Usage Examples

### Using the Manager (Recommended)

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException

client = Client(
    ...
)

# Get a specific user
try:
    user = client.users.get_by_id(user_id=12345)
    print(f"User: {user.login}")
    print(f"Name: {user.first_name} {user.last_name}")
    print(f"Email: {user.email}")
    print(f"Alumni: {user.alumni}")

    # Access image properties directly (no dict notation needed)
    print(f"Profile Image: {user.image.link}")
    print(f"Large Image: {user.image.large}")
    print(f"Medium Image: {user.image.medium}")
except FortyTwoNotFoundException:
    print("User not found")

# Get all users with pagination
users = client.users.get_all(page=1, page_size=50)
for user in users:
    print(f"{user.id}: {user.login}")
```

### Using Resources Directly

```python
from fortytwo.resources.user.resource import GetUserById, GetUsers

# Get a specific user
user = client.request(GetUserById(12345))

# Get all users
users = client.request(GetUsers())
```

## Data Structure

### User JSON Response
```json
{
  "id": 132246,
  "email": "lhutt@student.42mulhouse.fr",
  "login": "lhutt",
  "first_name": "Lucas",
  "last_name": "Hutt",
  "usual_full_name": "Lucas Hutt",
  "usual_first_name": null,
  "url": "https://api.intra.42.fr/v2/users/lhutt",
  "phone": "hidden",
  "displayname": "Lucas Hutt",
  "kind": "student",
  "image": {
    "link": "https://cdn.intra.42.fr/users/532a41a8ebd802b8c50a646af4c6d372/lhutt.jpg",
    "versions": {
      "large": "https://cdn.intra.42.fr/users/299e97d67bda6470995aba30b0855fe4/large_lhutt.jpg",
      "medium": "https://cdn.intra.42.fr/users/984b35f383432790e47847f972f37074/medium_lhutt.jpg",
      "small": "https://cdn.intra.42.fr/users/7734f15a32e8c5828c21ae43bbf1480b/small_lhutt.jpg",
      "micro": "https://cdn.intra.42.fr/users/63c521fd0e57a62157705e1fa0e99d33/micro_lhutt.jpg"
    }
  },
  "staff?": false,
  "correction_point": 12,
  "pool_month": "september",
  "pool_year": "2022",
  "location": null,
  "wallet": 87,
  "anonymize_date": "2028-10-03T00:00:00.000+02:00",
  "data_erasure_date": "2028-10-03T00:00:00.000+02:00",
  "created_at": "2022-08-26T09:32:41.327Z",
  "updated_at": "2025-10-03T23:02:48.726Z",
  "alumnized_at": null,
  "alumni?": false,
  "active?": true,
  "cursus_users": [...],
  "projects_users": [...],
  "campus": [...],
  "campus_users": [...]
}
```

## Parameters

For detailed information about filtering, sorting, and ranging user queries, see the [User Parameters Documentation](parameter/README.md).

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
    user = client.users.get_by_id(user_id=99999)
    print(f"Found user: {user.login}")
except FortyTwoNotFoundException:
    print("User not found")
except FortyTwoUnauthorizedException:
    print("Authentication failed")
except FortyTwoRateLimitException as e:
    print(f"Rate limit exceeded. Wait {e.wait_time} seconds")
except FortyTwoNetworkException:
    print("Network error occurred")
except FortyTwoRequestException as e:
    print(f"Request failed: {e}")
```

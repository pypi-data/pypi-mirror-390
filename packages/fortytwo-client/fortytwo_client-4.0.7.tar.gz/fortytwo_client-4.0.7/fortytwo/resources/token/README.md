# Token Resource

The Token resource provides access to OAuth2 token information and validation for the 42 School API.

## Overview

This module allows you to inspect and validate OAuth2 tokens used for authenticating with the 42 API, including token metadata, scopes, expiration, and application information.

## Classes

### `Token`
Represents OAuth2 token information and metadata.

**Properties:**
- `owner` (Optional[int]): Resource owner ID (user ID who authorized the token, None for client credentials)
- `scopes` (List[str]): List of granted permissions/scopes
- `expires` (int): Token expiration time in seconds from now
- `uid` (str): Application UID that owns this token

### Resource Classes

#### `GetToken`
Fetches information about the current access token.
- **Endpoint:** `https://api.intra.42.fr/oauth/token/info`
- **Method:** GET
- **Returns:** `Token`

## Usage Examples

### Using the Manager (Recommended)

```python
from fortytwo import Client

client = Client(
    ...
)

# Get current token information
token_info = client.tokens.get()
if token_info:
    print(f"Application UID: {token_info.uid}")
    print(f"Expires in: {token_info.expires} seconds")
    print(f"Scopes: {', '.join(token_info.scopes)}")

    if token_info.owner:
        print(f"Authorized by user: {token_info.owner}")
    else:
        print("Client credentials token (no user)")
```

### Using Resources Directly

```python
from fortytwo.resources.token.resource import GetToken

# Get token information
token_info = client.request(GetToken())
```

## Data Structure

### Token Info JSON Response
```json
{
  "resource_owner_id": 12345,
  "scopes": ["public", "projects", "profile"],
  "expires_in_seconds": 7200,
  "application": {
    "uid": "your-app-uid-here"
  }
}
```

## Error Handling

Methods raise exceptions on errors:

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoUnauthorizedException, FortyTwoRequestException

client = Client(
    ...
)

try:
    token_info = client.tokens.get()
    print(f"Token expires in {token_info.expires} seconds")
    print(f"Scopes: {', '.join(token_info.scopes)}")
except FortyTwoUnauthorizedException:
    print("Token is invalid or expired")
except FortyTwoRequestException as e:
    print(f"Unable to retrieve token information: {e}")
```

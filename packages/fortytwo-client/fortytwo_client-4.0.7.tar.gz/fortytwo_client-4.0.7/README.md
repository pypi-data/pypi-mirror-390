# FortyTwo Client

A Python client library for the 42 School API that simplifies authentication and data retrieval.

## Features

- 🔐 **Easy authentication** - OAuth2 handled automatically
- 📊 **Resource managers** - Convenient methods for users, projects, campuses, cursuses, cursus users, locations, teams, and more
- 🔑 **Secret management** - Flexible credential storage (Memory, HashiCorp Vault)
- 🛡️ **Error handling** - Automatic retry and error management
- 📝 **Type hints** - Full type annotation support
- ⚙️ **Customizable** - Flexible configuration and parameters
- 🔄 **Pagination** - Easy iteration over paginated results

## Installation

### From PyPI (recommended)

```bash
# Using pip
pip install fortytwo-client

# Using uv (recommended)
uv add fortytwo-client
```

### From source

```bash
git clone https://github.com/lucas-ht/fortytwo-client.git
cd fortytwo-client
uv sync
```

### Development installation

```bash
git clone https://github.com/lucas-ht/fortytwo-client.git
cd fortytwo-client
uv sync --group dev
```

## Quick Start

### 1. Get your API credentials

First, you need to create an application on the [42 API](https://api.intra.42.fr/apidoc) to get your client ID and secret.

### 2. Basic usage

```python
from fortytwo import Client

# Create client instance with credentials
client = Client(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Fetch user information
user = client.users.get_by_id(user_id=12345)
print(f"User: {user.id}")
print(f"User: {user['login']}")

# Fetch projects
projects = client.projects.get_by_cursus_id(cursus_id=21)

# Fetch campus information
campus = client.campuses.get_by_id(campus_id=1)
print(f"Campus: {campus.name} ({campus.city}, {campus.country})")

# Fetch cursus information
cursus = client.cursuses.get_by_id(cursus_id=2)
print(f"Cursus: {cursus.name}")
```

### 3. Advanced usage with custom parameters

```python
from fortytwo import Client, parameter

client = Client(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Use custom parameters for filtering
users = client.users.get_all(
    parameter.UserParameters.Filter.by_login("jdoe"),
)
```

### 4. Pagination support

All manager methods that return lists support pagination through `page` and `page_size` keyword arguments:

```python
from fortytwo import Client

client = Client(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Fetch first page with 50 items
users = client.users.get_all(page=1, page_size=50)

# Fetch second page
users_page2 = client.users.get_all(page=2, page_size=50)

# Works with all list-returning methods
projects = client.projects.get_by_cursus_id(21, page=1, page_size=25)
campuses = client.campuses.get_all(page=1, page_size=50)
cursuses = client.cursuses.get_all(page=1, page_size=50)
locations = client.locations.get_by_user_id(12345, page=1, page_size=100)
project_users = client.project_users.get_by_project_id(1337, page=2, page_size=50)

# Iterate through all pages
all_users = []
page = 1
while True:
    users = client.users.get_all(page=page, page_size=100)
    if not users:
        break
    all_users.extend(users)
    if len(users) < 100:  # Last page
        break
    page += 1
```

**Pagination parameters:**
- `page` (int, optional): Page number to fetch (1-indexed)
- `page_size` (int, optional): Number of items per page (1-100)

> [!NOTE]
> The `page_size` parameter must be between 1 and 100, as enforced by the 42 API.

### 5. Error handling

The library raises exceptions for failed requests. Always use try-catch blocks to handle potential errors:

```python
from fortytwo import Client
from fortytwo.exceptions import (
    FortyTwoClientException,
    FortyTwoNotFoundException,
    FortyTwoRateLimitException,
    FortyTwoNetworkException,
    FortyTwoUnauthorizedException,
)

client = Client(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

try:
    user = client.users.get_by_id(user_id=12345)
    print(f"User: {user.login}")
except FortyTwoNotFoundException:
    print("User not found")
except FortyTwoUnauthorizedException:
    print("Authentication failed")
except FortyTwoRateLimitException as e:
    print(f"Rate limit exceeded. Wait {e.wait_time} seconds")
except FortyTwoNetworkException:
    print("Network error occurred")
except FortyTwoClientException as e:
    print(f"Request failed: {e}")
```

**Available exceptions:**
- `FortyTwoClientException` - Base exception for all client errors
- `FortyTwoAuthException` - Authentication-related errors
- `FortyTwoRequestException` - General request errors
- `FortyTwoRateLimitException` - Rate limit exceeded (includes `wait_time` attribute)
- `FortyTwoNetworkException` - Network connectivity issues
- `FortyTwoParsingException` - Response parsing failures
- `FortyTwoNotFoundException` - Resource not found (404)
- `FortyTwoUnauthorizedException` - Unauthorized access (401)
- `FortyTwoServerException` - Server errors (5xx)


## Examples

See the `example/` directory for more detailed usage examples:

- [`fetch_user_by_id.py`](example/fetch_user_by_id.py) - Fetching user information by ID
- [`fetch_user_by_login.py`](example/fetch_user_by_login.py) - Fetching user information by login
- [`fetch_project.py`](example/fetch_project.py) - Working with projects
- [`fetch_location.py`](example/fetch_location.py) - Location data retrieval
- [`fetch_cursus_user_by_login.py`](example/fetch_cursus_user_by_login.py) - Fetching cursus users for a user
- [`fetch_teams_by_login.py`](example/fetch_teams_by_login.py) - Fetching teams for a user
- [`pagination_example.py`](example/pagination_example.py) - Using pagination to fetch data across multiple pages
- [`vault_secret_manager.py`](example/vault_secret_manager.py) - HashiCorp Vault secret management

## Documentation

### Core Features

- **[Resources Overview](fortytwo/resources/README.md)** - API resource documentation
- **[Secret Manager](fortytwo/request/secret_manager/README.md)** - Credential management strategies (Memory, Vault)

### API Resources

The client provides managers for accessing different 42 API resources:

- **[Users](fortytwo/resources/user/README.md)** - `client.users.*` - User information and profiles
- **[Projects](fortytwo/resources/project/README.md)** - `client.projects.*` - Project data and details
- **[Campuses](fortytwo/resources/campus/README.md)** - `client.campuses.*` - Campus information and locations
- **[Campus Users](fortytwo/resources/campus_user/README.md)** - `client.campus_users.*` - User associations with campuses
- **[Cursuses](fortytwo/resources/cursus/README.md)** - `client.cursuses.*` - Cursus (curriculum) information
- **[Cursus Users](fortytwo/resources/cursus_user/README.md)** - `client.cursus_users.*` - User enrollments in cursuses
- **[Locations](fortytwo/resources/location/README.md)** - `client.locations.*` - Campus location tracking
- **[Project Users](fortytwo/resources/project_user/README.md)** - `client.project_users.*` - User-project relationships
- **[Teams](fortytwo/resources/team/README.md)** - `client.teams.*` - Team information and members
- **[Tokens](fortytwo/resources/token/README.md)** - `client.tokens.*` - API token management

Each resource manager provides methods like:
- `get_by_id(id)` - Fetch a single resource by ID
- `get_all(*params)` - Fetch multiple resources with filtering
- Custom methods specific to each resource type

See individual resource documentation in [`fortytwo/resources/`](fortytwo/resources/) for details.

## Advanced Configuration

### Secret Management

The client supports multiple secret storage backends:

```python
from fortytwo import Client
import hvac

# Memory-based secrets (default)
client = Client(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# HashiCorp Vault integration
vault_client = hvac.Client(url='https://vault.example.com', token='...')
config = Client.Config(
    secret_manager=Client.SecretManager.Vault(
        vault_client=vault_client,
        secret_path='fortytwo/api'
    )
)
client = Client(config=config)
```

See [Secret Manager Documentation](fortytwo/request/secret_manager/README.md) for details.

### Logging Configuration

The library uses Python's standard logging module. By default, it uses a `NullHandler` to avoid interfering with your application's logging configuration.

See [Logger Documentation](fortytwo/logger/README.md) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see the LICENSE file for details.

## Links

- [42 API Documentation](https://api.intra.42.fr/apidoc)
- [GitHub Repository](https://github.com/lucas-ht/fortytwo-client)
- [Issue Tracker](https://github.com/lucas-ht/fortytwo-client/issues)

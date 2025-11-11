# 42 Client Resources

This directory contains all the resource modules for interacting with the 42 School API. Each resource provides both low-level API access and high-level manager interfaces.

## 📁 Resource Directory Structure

```
resources/
├── user/           # User profiles and authentication
├── project/        # Curriculum projects and metadata
├── project_user/   # Project completion and grading data
├── location/       # Campus workstation and session tracking
├── campus/         # Campus information and locations
├── campus_user/    # User associations with campuses
├── cursus/         # Cursus (curriculum) information
├── cursus_user/    # User enrollments in cursuses
├── team/           # Team information and members
├── token/          # OAuth2 token information and validation
└── custom.py       # Custom resource implementations
```

## 🚀 Quick Start

### Using Managers (Recommended)
The easiest way to interact with resources is through the client managers:

```python
from fortytwo import Client

client = Client(
    ...
)

# User operations
user = client.users.get_by_id(user_id=12345)
users = client.users.get_all()

# Project operations
project = client.projects.get_by_id(project_id=1)
projects = client.projects.get_all()

# Campus operations
campus = client.campuses.get_by_id(campus_id=1)
campuses = client.campuses.get_all()

# Campus user operations
campus_users = client.campus_users.get_by_user_id(user_id=12345)

# Cursus operations
cursus = client.cursuses.get_by_id(cursus_id=2)
cursuses = client.cursuses.get_all()

# Cursus user operations
cursus_users = client.cursus_users.get_by_user_id(user_id=12345)

# Location tracking
locations = client.locations.get_by_user_id(user_id=12345)

# Project completions
completions = client.project_users.get_all()

# Team operations
teams = client.teams.get_by_user_id(user_id=12345)

# Token validation
token_info = client.tokens.get()
```

### Using Resources Directly
For fine-grained control, use resource classes directly:

```python
from fortytwo.resources.user.resource import GetUserById
from fortytwo.resources.project.resource import GetProjects

# Direct resource usage
user = client.request(GetUserById(12345))
projects = client.request(GetProjects())
```

## 📚 Resource Documentation

Each resource directory contains detailed documentation:

* [User Resource](user/README.md)
* [Project Resource](project/README.md)
* [Project User Resource](project_user/README.md)
* [Location Resource](location/README.md)
* [Campus Resource](campus/README.md)
* [Campus User Resource](campus_user/README.md)
* [Cursus Resource](cursus/README.md)
* [Cursus User Resource](cursus_user/README.md)
* [Team Resource](team/README.md)
* [Token Resource](token/README.md)

## 🔧 Common Patterns

### Error Handling
All resource methods raise exceptions on errors:

```python
from fortytwo import Client
from fortytwo.exceptions import FortyTwoNotFoundException, FortyTwoRequestException

client = Client(
    ...
)

try:
    user = client.users.get_by_id(user_id=12345)
    print(f"Found user: {user.login}")
except FortyTwoNotFoundException:
    print("User not found")
except FortyTwoRequestException as e:
    print(f"Request failed: {e}")
```

### Pagination
All list-returning methods support pagination:

```python
# Fetch specific page
users = client.users.get_all(page=1, page_size=50)

# Iterate through all pages
page = 1
all_users = []
while True:
    users = client.users.get_all(page=page, page_size=100)
    if not users:
        break
    all_users.extend(users)
    if len(users) < 100:
        break
    page += 1
```

### Data Serialization
All resource objects support JSON serialization:

```python
import json
from fortytwo.json import default_serializer

client = Client(
    ...
)

user = client.users.get_by_id(user_id=12345)
user_json = json.dumps(user, default=default_serializer, indent=2)
```

## 🏗️ Architecture Overview

### Resource Classes
Low-level classes that map directly to API endpoints:
- Handle HTTP requests and responses
- Parse JSON data into Python objects
- Provide type-safe interfaces

### Manager Classes
High-level interfaces for common operations:
- Convenient method names (`get`, `get_all`, etc.)
- Parameter validation and defaults
- Consistent error handling

### Data Models
Python classes representing API entities:
- Type-safe property access
- Automatic JSON serialization
- Datetime parsing and formatting

## 🤝 Contributing

When adding new resources:

1. Create a new directory under `resources/`
2. Implement the data model class
3. Create resource classes for API endpoints
4. Add a manager class for convenience methods

## 📖 API Reference

For complete API documentation, see:
- [42 API Documentation](https://api.intra.42.fr/apidoc)
- Individual resource README files in each directory
- Inline code documentation and type hints

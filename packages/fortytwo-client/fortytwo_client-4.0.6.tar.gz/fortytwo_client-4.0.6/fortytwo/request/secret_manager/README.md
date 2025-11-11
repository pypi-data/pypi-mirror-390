# Secret Manager

The Secret Manager provides a flexible strategy pattern for managing 42 API credentials. This allows you to store secrets in different backends depending on your security requirements and infrastructure.

## Overview

The 42 API requires OAuth2 credentials (client ID and client secret) for authentication. The Secret Manager abstracts how these credentials are stored and retrieved, supporting:

- ✅ **In-memory storage** - Simple and fast
- ✅ **HashiCorp Vault** - Enterprise secret management
- ✅ **Custom implementations** - Integrate with any secret backend

## Available Implementations

### MemorySecretManager

Stores credentials in memory. This is the **default implementation** and provides backward compatibility.

**Pros:**
- No external dependencies
- Simple and straightforward
- Good for development and testing
- Fast credential access

**Cons:**
- Secrets must be provided at initialization
- No automatic secret rotation
- Secrets visible in process memory

**Usage:**
```python
from fortytwo import Client

# Method 1: Direct credentials (uses MemorySecretManager internally)
client = Client(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Method 2: Explicit memory secret manager
config = Client.Config(
    secret_manager=Client.SecretManager.Memory(
        client_id="your_client_id",
        client_secret="your_client_secret"
    )
)
client = Client(config=config)
```

### VaultSecretManager

Retrieves credentials from HashiCorp Vault. Supports both KV v1 and v2 secrets engines.

**Pros:**
- Centralized secret management
- Automatic secret rotation support
- Audit logging of secret access
- Enterprise-grade security
- Integration with existing secret management infrastructure
- Secrets never stored in application code or environment

**Cons:**
- Requires Vault infrastructure
- Additional complexity
- Network dependency

**Requirements:**
```bash
pip install hvac
```

**Usage:**
```python
import hvac
from fortytwo import Client

# Initialize Vault client
vault_client = hvac.Client(
    url='https://vault.example.com:8200',
    token='your-vault-token'
)

# Create Vault secret manager
vault_secret_manager = Client.SecretManager.Vault(
    vault_client=vault_client,
    secret_path='fortytwo/api',  # Path to secret in Vault
    mount_point='secret',  # KV mount point
)

# Use with FortyTwo client
config = Client.Config(secret_manager=vault_secret_manager)
client = Client(config=config)
```

## Configuration Parameters

### MemorySecretManager Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | `str` | Yes | Your 42 API client ID |
| `client_secret` | `str` | Yes | Your 42 API client secret |

### VaultSecretManager Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vault_client` | `hvac.Client` | Required | Authenticated Vault client instance |
| `secret_path` | `str` | Required | Path to secret in Vault (e.g., "fortytwo/api") |
| `mount_point` | `str` | `"secret"` | KV secrets engine mount point |

## Vault Setup

### Secret Format

Your secret in Vault must contain these fields:

```json
{
  "client_id": "your_42_client_id",
  "client_secret": "your_42_client_secret"
}
```

### Vault Policies

Create a policy that allows your application to read the secrets:

```hcl
# fortytwo-api-policy.hcl
path "secret/data/fortytwo/api" {
  capabilities = ["read"]
}

# For KV v1:
path "secret/fortytwo/api" {
  capabilities = ["read"]
}
```

Apply the policy:

```bash
vault policy write fortytwo-api fortytwo-api-policy.hcl
```

## Secret Rotation

The `refresh_secrets()` method is called automatically when authentication fails (401 response). This enables automatic handling of rotated credentials:

### MemorySecretManager
Returns the same credentials (no rotation support)

### VaultSecretManager
Re-fetches secrets from Vault, supporting automatic rotation:

```python
# Your rotation process updates Vault
vault kv put secret/fortytwo/api \
    client_id="new_client_id" \
    client_secret="new_client_secret"

# FortyTwo client automatically detects and uses new credentials
# when the old ones fail (401 response)
```

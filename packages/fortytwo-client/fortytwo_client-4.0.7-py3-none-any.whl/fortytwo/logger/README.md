# Logging Guide

The `fortytwo` library uses Python's standard `logging` module to provide flexible and configurable logging capabilities. This guide explains how to configure and use logging in your applications.

## Quick Start

### Enable Debug Logging

The simplest way to see what the library is doing:

```python
from fortytwo import Client, logger

# Enable debug logging with a sensible default configuration
logger.enable_debug_logging()

client = Client(
    ...
)
```

This will output detailed logs including:
- API requests and responses
- Authentication token refresh events
- Rate limit information
- Error details with stack traces

### Disable Logging

For production environments where you don't want any library logs:

```python
from fortytwo import Client, logger

logger.disable_logging()

client = Client(
    ...
)
```

## Configuration Options

### Using the `configure_logger()` Function

The `configure_logger()` function provides a convenient way to set up logging:

```python
from fortytwo import logger
import logging

# Basic configuration with INFO level
logger.configure_logger(level=logging.INFO)

# Custom format string
logger.configure_logger(
    level=logging.DEBUG,
    format_string='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

# Custom handler (e.g., file logging)
file_handler = logging.FileHandler('fortytwo.log')
logger.configure_logger(level=logging.INFO, handler=file_handler)
```

**Parameters:**
- `level` (int): Logging level (e.g., `logging.DEBUG`, `logging.INFO`)
- `format_string` (str, optional): Custom format string for log messages
- `handler` (logging.Handler, optional): Custom handler to use

### Direct Logger Access

For full control, configure the logger directly:

```python
from fortytwo import logger
import logging

# Set the logging level
logger.logger.setLevel(logging.DEBUG)

# Add a custom handler
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.logger.addHandler(handler)

# Add multiple handlers
file_handler = logging.FileHandler('fortytwo_debug.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
))
logger.logger.addHandler(file_handler)
```

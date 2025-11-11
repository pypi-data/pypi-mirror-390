# CWS Logger Package

The `cws_helpers.logger` module provides an enhanced logging system with custom log levels, colored console output, and optional file logging. This guide explains how to use the logger in your projects.

## Features

- **Custom log levels** (FINE, STEP, SUCCESS) in addition to standard Python log levels
- **Colored console output** with level-specific formatting
- **Contextual logging** that automatically shows file, class, and function information
- **Detailed file logging** with rotation
- **Environment variable configuration** for log levels and context display options
- **Simple API** to quickly set up logging in any module

## Installation

The logger is part of the cws-helpers package. You can install it using pip without needing Poetry.

### Package Structure

The package uses a `src` layout, which means the actual package code is in the `src/cws_helpers` directory. When you install the package, the package will be available as `cws_helpers` in your Python environment:

```
cws-helpers/
├── src/
│   └── cws_helpers/  # This becomes the importable package
│       ├── __init__.py
│       └── logger/
│           ├── __init__.py
│           └── logger.py
└── ...
```

### For Users: Installing with pip

You can install directly from the GitHub repository:

```bash
# Install the latest version
pip install git+https://github.com/caseywschmid/cws-helpers.git

# Install a specific version using a tag (once tags are available)
pip install git+https://github.com/caseywschmid/cws-helpers.git@v0.1.0
```

### For requirements.txt

If you need to include the package in a requirements.txt file:

```text
# For the latest version
git+https://github.com/caseywschmid/cws-helpers.git

# For a specific version
git+https://github.com/caseywschmid/cws-helpers.git@v0.1.0
```

### For Developers: Using Poetry

If you're contributing to the project or modifying the code, you'll need Poetry:

```bash
# Clone the repository
git clone https://github.com/caseywschmid/cws-helpers.git

# Navigate to the project directory
cd cws-helpers

# Install dependencies using Poetry
poetry install
```

## Basic Usage

Here's how to use the logger in your Python modules:

```python
from cws_helpers.logger import configure_logging

# Configure logging for this module
log = configure_logging(__name__)

# Use standard log levels
log.debug("Debug message")
log.info("Info message")
log.warning("Warning message")
log.error("Error message")
log.critical("Critical message")

# Use custom log levels
log.fine("Fine-level message")
log.step("Step-level message")
log.success("Success message")
```

## Log Levels

The logger provides three custom log levels in addition to Python's standard levels:

| Level       | Value  | Description                                                                           |
| ----------- | ------ | ------------------------------------------------------------------------------------- |
| DEBUG       | 10     | Detailed debugging information                                                        |
| **FINE**    | **15** | Less verbose than DEBUG, but more detailed than INFO                                  |
| INFO        | 20     | Confirmation that things are working as expected                                      |
| **SUCCESS** | **22** | Successful operations (with green formatting)                                         |
| **STEP**    | **25** | Major steps in program execution (with purple formatting)                             |
| WARNING     | 30     | Indication that something unexpected happened                                         |
| ERROR       | 40     | Due to a more serious problem, the software hasn't been able to perform a function    |
| CRITICAL    | 50     | A serious error, indicating that the program itself may be unable to continue running |

The custom levels provide more granularity for your logging needs.

## Configuration Options

### Basic Configuration

The `configure_logging` function accepts several parameters:

```python
from cws_helpers.logger import configure_logging

# Basic configuration with default settings
log = configure_logging(__name__)

# Configure with explicit log level
import logging
log = configure_logging(__name__, log_level=logging.INFO)

# Enable file logging
log = configure_logging(__name__, keep_logs=True)

# Specify custom log directory
log = configure_logging(__name__, keep_logs=True, log_dir="my_logs")
```

### Full Configuration Options

```python
def configure_logging(
    logger_name="root",      # Name of the logger (typically __name__)
    log_level=None,          # Log level (if None, reads from environment)
    keep_logs=False,         # Whether to write logs to file
    log_dir="logs"           # Directory for log files
):
    """Configure and return a logger with custom formatting."""
    # ...
```

## Environment Variables

The logger respects the following environment variables:

- `LOG_LEVEL`: Numeric log level (default: 15 for FINE)
- `CONTEXT_DISPLAY`: Controls how contextual information is displayed in logs:
  - `none`: No contextual information (default)
  - `function`: Shows only the function name - `[function_name()]`
  - `class_function`: Shows class and function name - `[ClassName.function_name()]`
  - `full`: Shows complete context - `[ClassName.function_name() in module.py:42]`

Example `.env` file:

```
LOG_LEVEL=10
CONTEXT_DISPLAY=class_function
```

## Colored Console Output

The logger automatically formats console output with color-coded levels:

- **DEBUG**: Gray
- **FINE**: Blue
- **INFO**: Green
- **SUCCESS**: Green with ★ symbol (includes separator lines)
- **STEP**: Purple
- **WARNING**: Yellow
- **ERROR**: Red
- **CRITICAL**: Bold Red

## File Logging

When `keep_logs=True`, the logger writes detailed logs to files:

- Logs are stored in the specified `log_dir` (default: "logs")
- Log files include full timestamps, level names, and source information
- Files rotate when they reach 5MB (keeping 3 backup files)

The file format is:

```
2025-03-09 14:35:22 [INFO] module_name: Log message (file.py:123)
```

## Direct Logger Access

If you need to access a logger that's already been configured:

```python
import logging

# Get a preconfigured logger
log = logging.getLogger(__name__)
```

## Complete Example

Here's a complete example showing how to use the logger in a project:

```python
# myapp/utils.py
from cws_helpers.logger import configure_logging

log = configure_logging(__name__)

def process_data(data):
    log.fine(f"Processing data: {data[:30]}...")

    try:
        # Log a major step
        log.step("Beginning data transformation")
        result = transform_data(data)

        # Log success
        log.success(f"Successfully processed {len(data)} bytes of data")
        return result
    except Exception as e:
        log.error(f"Failed to process data: {str(e)}")
        raise
```

## Advanced Usage: Creating a Custom Log Setup Function

For consistency across your application, you might want to create a utility function:

```python
# myapp/log_utils.py
from cws_helpers.logger import configure_logging

def setup_logger(module_name):
    """
    Standard logger setup for this application.

    Args:
        module_name: The module name (usually __name__)

    Returns:
        The configured logger
    """
    return configure_logging(
        logger_name=module_name,
        keep_logs=True,
        log_dir="app_logs"
    )
```

Then in your modules:

```python
# myapp/some_module.py
from myapp.log_utils import setup_logger

logger = setup_logger(__name__)
logger.info("Module initialized")
```

## Contextual Logging

The logger can automatically include contextual information about where each log message originates, eliminating the need to manually add this information to your log messages.

This feature is controlled by the `CONTEXT_DISPLAY` environment variable:

```python
# Instead of manually typing context:
log.info("[UserService] Creating new user...")

# With CONTEXT_DISPLAY=class_function, this is automatic:
log.info("Creating new user...")  # Will show: INFO:   Creating new user...           [UserService.create_user()]
```

The contextual information is right-aligned in the terminal for cleaner presentation while preserving all relevant details.

### Contextual Display Options

1. **Function name only**:
   ```
   INFO:   Processing data...                      [process_data()]
   ```

2. **Class and function name**:
   ```
   INFO:   User created...                         [UserService.create_user()]
   ```

3. **Full context** (including file and line number):
   ```
   INFO:   Connecting to database...               [DatabaseManager.connect() in database.py:42]
   ```

## Tips and Best Practices

1. **Use the right level**: Reserve DEBUG for very detailed messages, use FINE for detailed but less verbose logging, INFO for general progress, and so on.

2. **Be specific in log messages**: Include relevant details but avoid sensitive information.

3. **Use contextual logging**: Leverage the `CONTEXT_DISPLAY` environment variable to automatically include source context instead of manually typing it in each log message.

4. **Use structured logging**: For complex data, consider formatting as JSON or using string templates:

   ```python
   logger.info(f"User {user_id} performed action {action} on resource {resource_id}")
   ```

5. **Log at the beginning and end of important operations**:

   ```python
   logger.fine(f"Starting import of file {filename}")
   # ... do import ...
   logger.success(f"Completed import of {count} records from {filename}")
   ```

6. **Use STEP for workflow tracking**: The STEP level is perfect for indicating major phases of execution:

   ```python
   logger.step("Phase 1: Data collection")
   # ... collection code ...
   logger.step("Phase 2: Data processing")
   # ... processing code ...
   ```

7. **Include context in ERROR logs**: Make sure error logs include enough information to diagnose the problem:
   ```python
   except Exception as e:
       logger.error(f"Failed to process order {order_id}: {str(e)}", exc_info=True)
   ```

## Troubleshooting

**Problem**: No console output is visible.  
**Solution**: Check that your log level is not set too high. If LOG_LEVEL is set to 30, debug/fine/info messages won't show.

**Problem**: Colors don't appear in console output.  
**Solution**: Some terminals don't support ANSI color codes. Try running in a different terminal.

**Problem**: Log files aren't being created.  
**Solution**: Ensure you've set `keep_logs=True` and that the application has write permission to the log directory.

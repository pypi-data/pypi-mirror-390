# LY001: Exception exc_info

### Enforce `exc_info=True` in exception handlers

## Problem

Logging exceptions without `exc_info=True` loses critical debugging information:

```python
try:
    result = api.fetch_user(user_id)
except Exception:
    logger.error("Failed to fetch user")
```

This produces a log entry with only the message:
```
ERROR - Failed to fetch user
```

Missing information:
- Exception type (ConnectionError? ValueError? TimeoutError?)
- Exact location in the code where the exception occurred
- Full call stack trace showing the execution path
- Root cause context

## Solution

Add `exc_info=True` to include the full stack trace:

```python
try:
    result = api.fetch_user(user_id)
except Exception:
    logger.error("Failed to fetch user", exc_info=True)
```

The log now includes the complete context:
```
ERROR - Failed to fetch user
Traceback (most recent call last):
  File "app.py", line 42, in fetch_user
    response = requests.get(url)
  ...
ConnectionError: Connection refused
```

The stack trace reveals exactly where and why the exception occurred.

## Benefits

With stack traces included:
- Faster incident resolution (minutes vs hours)
- Root cause immediately visible in logs
- No need to reproduce errors in production
- Reduced debugging time and team coordination

## Configuration

```yaml
exception_exc_info:
  levels: [error]  # Check error logs only
  severity: fail   # Block CI if violations found
```

### Options

**`levels`**: Which log levels to enforce

- `[error]` - Only error logs (recommended)
- `[error, warning]` - Error and warning logs
- `[any]` - All log levels

**`severity`**: Violation handling

- `fail` - Exit with error (recommended for CI)
- `warn` - Print warning only
- `info` - Informational

## Examples

### Pass

```python
# With exc_info=True
try:
    connect_db()
except Exception:
    logger.error("DB connection failed", exc_info=True)

# With logger.exception() - automatically includes exc_info=True
try:
    connect_db()
except Exception:
    logger.exception("DB connection failed")

# Non-exception context
if not user:
    logger.error("User not found")  # No exception to trace
```

### Fail

```python
# Missing exc_info in exception handler
try:
    process_payment()
except Exception:
    logger.error("Payment failed")  # No stack trace

# String formatting loses the trace
try:
    load_config()
except Exception as e:
    logger.error(f"Config error: {e}")  # Only the message is logged
```
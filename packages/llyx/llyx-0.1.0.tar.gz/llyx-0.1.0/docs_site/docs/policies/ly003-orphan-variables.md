# LY003: Orphan Variables

### Ensure variables in logs are explicitly associated with a key

## Problem

Variables logged without keys make logs impossible to parse or monitor:

```python
logger.error(f"Error occurred {error}")
logger.error("Failed with %s", status_code)
```

This prevents:
- Indexing by log aggregators (values cannot be extracted)
- Structured logging and key-value parsing
- Automated monitoring and alerting based on field values


## Solution

Prefix every variable with a key and the configured delimiter:

```python
# f-strings
logger.error(f"error={error}")
logger.error(f"status={status_code} message={msg}")

# % formatting
logger.error("error=%s", error)
logger.error("status=%s message=%s", status_code, msg)

# Debug syntax (Python 3.8+)
logger.error(f"Failed {result=}")
```

## Benefits

With structured key-value logging:
- Fields can be indexed and queried by key
- Monitoring and alerting tools can extract specific values
- Log aggregation systems can parse and aggregate by field
- Dashboards can track metrics and trends

## Configuration

```yaml
consistent_kv:
  delimiter: "="
  levels: [any]
  severity: fail
```

### Options

**`delimiter`**: The separator between key and variable

- `"="` - Standard key=value (recommended)
- `":"` - Alternative key:value
- Custom string - Use any separator

**`levels`**: Which log levels to enforce

- `[any]` - All levels (recommended)
- `[error, warning]` - Specific levels only
- `[error]` - Just error logs

**`severity`**: Violation handling

- `fail` - Exit with error (recommended for CI)
- `warn` - Print warning only

## Examples

### Pass

```python
# Static strings (no variables)
logger.error("Database connection failed")

# f-string with key
logger.error(f"user_id={user_id}")
logger.error(f"user_id={user_id} status={status}")

# % formatting with key
logger.error("user_id=%s", user_id)
logger.error("user_id=%s status=%s", user_id, status)

# Debug syntax (Python 3.8+)
logger.error(f"result={result=}")
```

### Fail

```python
# Variable without key
logger.error(f"Error occurred {error}")
logger.error(f"user_id={user_id} status {status}")

# % formatting without key
logger.error("Error: %s", error)
logger.error("Failed with %s", status_code)

# Wrong delimiter
logger.error(f"user_id:{user_id}")  # Configured for "=" not ":"
```
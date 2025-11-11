# Feature - Consistent Logger Names

Active: False

Policy: consistent_logger_name
Policy_ID: LY004
Type: Structural
is_llm: False

## What it does

Enforces the use of `__name__` for logger instantiation instead of hardcoded strings. This ensures:
- Module-specific logger names for better filtering
- Proper logger hierarchy for configuration
- Easier debugging and log routing
- Python logging best practices

## Why it matters

**Problem:** Hardcoded logger names break the logger hierarchy and make it difficult to:
- Configure logging at different levels per module
- Filter logs by package/module
- Understand where logs originate from

## Examples

### PASS: Using `__name__`
```python
import logging

logger = logging.getLogger(__name__)

log = logging.getLogger(__name__)

class MyClass:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
```

### FAIL: Hardcoded string literals
```python
import logging

logger = logging.getLogger("airflow.utils.log")

logger = logging.getLogger("MyClass")

logger = logging.getLogger("mycustomlogger")

logger = logging.getLogger("celery.app.trace")
```

## Benefits

1. **Automatic hierarchy:** `__name__` resolves to `package.module.submodule`
2. **Easy filtering:** Configure logging like `logging.getLogger('airflow.models').setLevel(DEBUG)`
3. **Better traceability:** Log records show actual module origin
4. **Refactoring-safe:** Module renames automatically update logger names

## Configuration

```yaml
logger_names: [logger, logging, log]

consistent_logger_names:
  severity: fail
```
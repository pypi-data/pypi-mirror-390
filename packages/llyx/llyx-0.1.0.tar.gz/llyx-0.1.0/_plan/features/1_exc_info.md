# Feature - exc_info=True for exceptions

Active: True

Policy: exc_info=True when logging within exception try/catch block
Policy_ID: LY001
Type: Structural
is_llm: False

What it does: Enforces exc_info=True inside exception handlers to capture tracebacks.

Examples:

# FAIL: In except block without exc_info
```python
try:
    connect_db()
except Exception:
    logger.error("Connection failed")  # Missing exc_info=True
```

# PASS: Has exc_info=True
```python
try:
    connect_db()
except Exception:
    logger.error("Connection failed", exc_info=True)
```

# PASS: Outside except block (not enforced)
```python
if error:
    logger.error("Something wrong")  # No violation
Configuration:
```

```yaml
ERROR:
  must_have_exc_info: {}
```
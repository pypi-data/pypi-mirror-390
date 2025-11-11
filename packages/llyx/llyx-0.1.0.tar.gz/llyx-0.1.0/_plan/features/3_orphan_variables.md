# Feature - LY003: orphan variables

Active: True

Policy: orphan variables (with consistent Key-Value Pairs)
Policy_ID: LY003
Type: Structural
is_llm: False

## What it does

Ensures that **any variable printed in a log message must be explicitly associated with a key** using the configured delimiter.

## Core Principle

- **Variables MUST have keys**: Any variable printed must be preceded by a key and the configured delimiter

## Examples

### PASS: Static string only (no variables)
```python
logger.error("Database connection failed")
logger.error("user_id=123 action=login")
```

### PASS: Variable with key (f-string)
```python
logger.error(f"user_id={user_id}")
logger.error(f"user_id={user_id} status={status}")
logger.error(f"Something went wrong key={value}")
```

### PASS: Variable with key (Python 3.8+ debug syntax)
```python
logger.error(f"Database write failed {result=}") 
```

### FAIL: Variable without key
```python
logger.error(f"Error occurred {error}")
logger.error(f"user_id={user_id} error {status}") 
```

### FAIL: Variable with wrong delimiter
```python
logger.error(f"user_id:{user_id}") 
```

### PASS: % formatting with key
```python
logger.error("user_id=%s", user_id)
logger.error("Something failed user_id=%s", user_id)
```

### FAIL: % formatting without key
```python
logger.error("Error: %s", error)
logger.error("Failed with %s", status_code)
```

## Configuration

```yaml
consistent_kv:
  delimiter: "="
  levels: ["any"]
  severity: fail
```
# LY002: Log Loop

### Prevent unconditional logging in hot loops

## Problem

Unconditional logging in loops creates excessive log volume:

```python
for user in users:
    logger.info(f"Processing user {user.id}")
    process_user(user)
```

With 10,000 items, this generates 10,000 log entries. In production:
- Disk space fills rapidly
- Log aggregation systems become overloaded
- Important error messages are buried in noise
- Performance degrades due to logging overhead

## Solution

Use conditional logging to limit entries:

```python
# Sample logging: log every 100th iteration
for i, user in enumerate(users):
    if i % 100 == 0:
        logger.info(f"Progress: {i}/{len(users)}")
    process_user(user)

# Or summarize before and after
logger.info(f"Processing {len(users)} users")
for user in users:
    process_user(user)
logger.info(f"Processed {len(users)} users successfully")
```

## Benefits

Conditional logging reduces overhead significantly:
- For 10,000 iterations: 100 logs instead of 10,000 (99% reduction)
- Logging overhead: ~1.5ms instead of ~150ms
- Reduced disk I/O and network bandwidth
- Lower log aggregation costs and faster query performance

## Configuration

```yaml
log_loop:
  levels: [info, debug]  # Check info and debug logs
  severity: fail         # Block CI if violations found
```

### Options

**`levels`**: Which log levels to check

- `[info, debug]` - Info and debug (recommended)
- `[any]` - All levels including error/warning
- `[debug]` - Only debug logs

**`severity`**: Violation handling

- `fail` - Exit with error (recommended for CI)
- `warn` - Print warning only
- `info` - Informational

## Examples

### Pass

```python
# Conditional logging: log every 100th iteration
for i, item in enumerate(items):
    if i % 100 == 0:
        logger.info(f"Progress: {i}/{len(items)}")
    process(item)

# Exception handler: always log exceptions
for item in items:
    try:
        process(item)
    except Exception:
        logger.error("Failed processing", exc_info=True)

# Conditional logging: log based on a condition
for user in users:
    if user.is_admin:
        logger.info(f"Processing admin: {user.id}")
    process(user)

# Summary logging: before and after the loop
logger.info(f"Starting batch of {len(items)} items")
for item in items:
    process(item)
logger.info("Batch complete")
```

### Fail

```python
# Unconditional logging in for-loop
for user in users:
    logger.info(f"Processing {user}")
    process(user)

# Unconditional logging in while-loop
while queue.has_items():
    item = queue.get()
    logger.debug(f"Got item: {item}")
    process(item)

# Unconditional logging in nested loop
for batch in batches:
    for item in batch:
        logger.info(f"Item: {item}")
        process(item)
```
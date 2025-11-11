# Feature - Avoid Logging in Hot Loops

Active: True

Policy: `log_loop` - Prevent logging in performance-critical loops
Policy_ID: LY002
Type: Performance
is_llm: False

## What it does
Detects and discourages logging statements inside hot loops (for/while). Logging in loops can:
- Blow up observability costs (thousands of log entries)
- Severely impact performance
- Create noise in log aggregation systems

## Detection Strategy
The policy flags violations when logging calls are:
1. Inside `for` or `while` loops
2. At specific log levels (configurable)
3. **Not conditionally gated** - i.e., will execute on every loop iteration

**Key principle**: If logging is wrapped in an `if` statement (including `try/except`), it's considered conditionally gated and passes the check.

## Examples

### FAIL: Logging in for loop
```python
for user in users:
    logger.info(f"Processing user {user.id}")
    process_user(user)
```
**Why it fails**: Logs once per user, could be thousands of entries

### FAIL: Logging in while loop
```python
while not connected:
    logger.warning("Waiting for connection...")
    time.sleep(1)
```
**Why it fails**: Potentially infinite log spam

### FAIL: Nested loop logging
```python
for batch in batches:
    for record in batch:
        logger.debug(f"Processing record {record.id}")
        process_record(record)
```
**Why it fails**: O(n²) logging statements

### PASS: Log before/after loop
```python
logger.info(f"Processing {len(users)} users")
for user in users:
    process_user(user)
logger.info("User processing complete")
```
**Why it passes**: Constant number of log entries

### PASS: Conditional logging in loop (rate-limiting)
```python
for i, user in enumerate(users):
    if i % 100 == 0:
        logger.info(f"Progress: {i}/{len(users)} users processed")
    process_user(user)
```
**Why it passes**: Rate-limited logging (every 100 iterations) - conditional check prevents log spam

### PASS: Conditional logging based on data
```python
for user in users:
    if user.is_premium:
        logger.info(f"Processing premium user {user.id}")
    process_user(user)
```
**Why it passes**: Conditional check limits logging to subset of iterations

### PASS: Error-only logging in loop (exception handler)
```python
for user in users:
    try:
        process_user(user)
    except Exception as e:
        logger.error(f"Failed to process user {user.id}", exc_info=True)
```
**Why it passes**: Exception handler is a conditional check - only logs on failures

## Configuration

```yaml
log_loop:
  levels: ["info", "debug"]  # Enforce on these levels in loops
  severity: "warn"           # Violation severity
```

### Configuration Options

- **`levels`**: Log levels to check (`["debug", "info", "warning", "error", "any"]`)
  - `"any"` - Check all log levels
  - Recommend: `["info", "debug"]` - Allow error/warning for exceptions

- **`severity`**: Violation severity (`"fail"` or `"warn"`)
  - `"fail"` - Block in CI/PR checks
  - `"warn"` - Report but don't block

### Opinionated Design

**Conditional logging is always allowed** - This is not configurable. The policy recognizes that:
- Rate-limited logging (`if i % 100 == 0`) is a valid pattern
- Conditional data checks (`if user.is_premium`) limit logging volume
- Exception handlers (`try/except`) are inherently conditional

This opinionated approach encourages proper logging practices without being overly restrictive.
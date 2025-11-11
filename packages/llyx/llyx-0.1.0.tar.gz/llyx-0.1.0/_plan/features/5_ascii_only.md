# Feature - ascii_only log messages

Active: True

Policy: no_emoji
Policy_ID: LY005
Type: Structural
is_llm: False

## What it does

Detects non-ASCII characters in log messages, including emojis (🚀, ✅) and special unicode symbols (→, ✓, •).

## Why it matters

**Breaks tooling and searchability:**
- Most log aggregation tools (Splunk, Datadog, ELK) struggle with unicode in search queries
- Terminal `grep` requires complex regex patterns or fails silently with unicode
- JSON serialization can fail or require special encoding
- Copy-paste from logs corrupts special characters, breaking runbook commands

**Best practice:** Logs are machine-first, human-second. Use ASCII alternatives: `=` not `→`.

## Examples

### Fail: Using → 
```python
logger.debug("Changed the status of job %s→%s", status_before, status_after)
```

## Configuration

```yaml
logger_names: [logger, logging, log]

no_emoji:
  severity: fail
```
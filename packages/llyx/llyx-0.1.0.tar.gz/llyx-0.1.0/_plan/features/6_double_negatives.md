# Feature - double negatives

Active: True

Policy: double_negatives
Policy_ID: LY006
Type: Structural
is_llm: True

## What it does

Detects presence of double negatives in log messages and suggest alternatives using LLM

## Why it matters

+**Semantic confusion and cognitive load:**
- Double negatives create ambiguous meaning ("removed ban on restricted" - is access now allowed or denied?)
- Harder to search and create alerts due to multiple phrasings of the same intent
- Increases cognitive load for on-call engineers debugging issues under time pressure
- Can lead to misinterpretation of system state in critical situations

**Best practice:** Use positive, direct phrasing in logs for clarity and searchability.

## Examples

### Fail
```python
logger.error("Market data feed removed ban on restricted symbol %s", symbol)
```

## Configuration

```yaml
logger_names: [logger, logging, log]

double_negatives:
  severity: warn
  levels: [any]
```
# Architecture: Policy Interface with kwargs

## Design Principle

**No defaults in the policy layer. Defaults belong in the configuration/schema layer.**

The policy interface accepts `**kwargs` for policy-specific parameters, but does NOT provide defaults. This separation of concerns ensures:
- ✅ Policies are generic and reusable
- ✅ Configuration logic is centralized
- ✅ Clear dependency flow: Config → Policy

---

## Updated Policy Interface

### Before
```python
@abstractmethod
def check(
    cls,
    code: str,
    file_path: Path,
    levels: List[str],
    logger_names: List[str]
) -> List[Dict]:
    pass
```

### After
```python
@abstractmethod
def check(
    cls,
    code: str,
    file_path: Path,
    levels: List[str],
    logger_names: List[str],
    **kwargs  # ← Policy-specific parameters
) -> List[Dict]:
    pass
```

---

## Files Modified

### 1. `src/loly/policies/base.py`
- ✅ Added `**kwargs` to abstract method signature
- ✅ Updated docstring to explain kwargs usage
- No defaults provided

### 2. `src/loly/policies/exception_exc_info.py`
- ✅ Updated `check()` signature to accept `**kwargs`
- Policy doesn't use kwargs (no policy-specific params)
- Maintains backward compatibility

### 3. `src/loly/policies/log_loop.py`
- ✅ Updated `check()` signature to accept `**kwargs`
- Policy doesn't use kwargs (no policy-specific params)
- Maintains backward compatibility

### 4. `src/loly/policies/consistent_kv.py`
- ✅ **Refactored to validate VARIABLES only** (not static strings)
- ✅ Extracts `delimiter` from kwargs (required)
- ✅ **No default** provided for delimiter
- ✅ Raises `ValueError` if delimiter is missing
- Message: "This should be provided by the configuration/schema layer"

---

## ConsistentKVPolicy: Variable-Based Validation

### Problem Solved

**Static string parsing is unreliable** due to ambiguity:
- "DB Error:" in text is confused with KV pairs
- Text with delimiters creates false positives
- Quoted values with spaces break regex patterns

### Solution: Focus on Variables

**Only validate variables** (the actual structured data being logged):
- F-strings: `f"user_id={user_id}"`
- % formatting: `"user_id=%s" % (user_id,)`
- Python 3.8+ debug syntax: `f"{user_id=}"`

**Static strings are skipped** entirely (no validation).

### Interface
```python
def check(
    code: str,
    file_path: Path,
    levels: List[str],
    logger_names: List[str],
    **kwargs  # Must contain: delimiter="="
) -> List[Dict]:
```

### Key Features
1. **No false positives**: Static text is never validated
2. **Variables mandatory**: Any variable must have an explicit key
3. **Delimiter enforcement**: Key-delimiter pattern must match config
4. **Multiple formats**: F-strings, % formatting, debug syntax
5. **No default delimiter**: Raises `ValueError` if not provided

### Usage
```python
# ✅ Correct: Delimiter provided from config layer
violations = ConsistentKVPolicy.check(
    code,
    Path("test.py"),
    ["error"],
    ["logger"],
    delimiter="="  # ← From schema/config layer
)

# ❌ Wrong: No delimiter (will raise ValueError)
violations = ConsistentKVPolicy.check(
    code,
    Path("test.py"),
    ["error"],
    ["logger"]
)
# ValueError: ConsistentKVPolicy requires 'delimiter' parameter in kwargs
```

---

## Configuration Layer Responsibility

The configuration/schema layer (e.g., `loly.yml`) provides:

```yaml
consistent_kv:
  delimiter: "="        # ← Default goes HERE, not in policy
  levels: ["error"]
  severity: fail
```

When linter calls the policy:
```python
config = load_config("loly.yml")  # Gets delimiter="="
ConsistentKVPolicy.check(
    code,
    file_path,
    config["levels"],
    config["logger_names"],
    delimiter=config["consistent_kv"]["delimiter"]  # ← Passed from config
)
```

---

## Architecture Flow

```
loly.yml (Configuration)
    ↓
    ├─ Load defaults: delimiter="="
    ├─ Load levels: ["error"]
    └─ Load logger_names: ["logger", "logging"]
        ↓
    Linter (Orchestration)
        ↓
        ├─ Extract config values
        └─ Call policy with kwargs
            ↓
    ConsistentKVPolicy.check(
        code,
        file_path,
        levels,
        logger_names,
        delimiter=config_value  # ← Required, from config
    )
        ↓
    Returns: List[Violations]
```

---

## Benefits

| Aspect | Benefit |
|--------|---------|
| **No False Positives** | Static text never validated, no confusion with delimiters in prose |
| **Reliability** | Clear, simple contract: variables must have keys |
| **Separation of Concerns** | Configuration logic in config layer, policy logic in policy layer |
| **Flexibility** | Easy to add new variable formats (f-strings, % formatting, debug syntax) |
| **Clarity** | Clear where defaults come from (config, not policy) |
| **Reusability** | Policies can be used with different configurations |
| **Composability** | Policies don't depend on config structure |
| **Testability** | Tests pass explicit kwargs, no hidden defaults |

---

## Testing

Tests explicitly provide required parameters:

```python
def test_valid_kv_with_equals_delimiter():
    code = '''logger.error("user_id=123 action=login")'''
    violations = ConsistentKVPolicy.check(
        code,
        Path("test.py"),
        ["error"],
        ["logger"],
        delimiter="="  # ← Explicit, no default
    )
    assert len(violations) == 0
```

---

## Next Steps

1. **Create config schema**: Define where defaults are stored
2. **Update linter**: Pass kwargs from config to policies
3. **Update configuration loader**: Extract policy-specific params
4. **Documentation**: Explain how to configure policies

---

## Summary

✅ **Policy interface**: Accepts `**kwargs` (no defaults)
✅ **ConsistentKVPolicy**: Requires `delimiter` from kwargs
✅ **Existing policies**: Updated for compatibility
✅ **Clear architecture**: Config → Policy flow

The policy layer stays generic and focused on validation logic. Configuration and defaults are managed at a higher layer.

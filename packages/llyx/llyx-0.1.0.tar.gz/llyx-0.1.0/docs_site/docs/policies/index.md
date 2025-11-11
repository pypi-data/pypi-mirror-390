# Policies

loly enforces logging best practices through policies. Think of them as guardrails between your code and the 3 AM incident that will haunt your dreams.

## Active Policies

These aren't suggestions. They're rules. Break them at your own peril.

| Code | Name | Severity | Your Fate |
|------|------|----------|-----------|
| [LY001](ly001-exception-exc-info.md) | Exception exc_info | Critical | No stack traces is no good |
| [LY002](ly002-log-loop.md) | Log Loop | Critical | Spammy logs = Angry ops teams |
| [LY003](ly003-orphan-variables.md) | Orphan Variables | Remove guesswork of what is in the logs | 

## Coming Soon (To Save You)

These are in development because apparently, nobody listens until they're already broken.

| Code | Name | Impact | ETA |
|------|------|--------|-----|

| **LY004** | Safe Serialization | Medium - Prevents explosion in production | Soon™ |
| **LY005** | Logger Naming | Medium - Better filtering, better debugging | Soon™ |

## Policy Philosophy

We believe in a simple approach:

**Actionable**: Every violation has a crystal-clear fix. No ambiguity. No excuses.

**Zero false positives**: We only flag genuine, production-grade problems. Not perfect, but real.

**Configurable**: Strict in CI, gentle in local development. Your choice.

**Performance-focused**: Static analysis only—we're not here to slow you down. Just stop you from breaking things.

## How Policies Work

Each policy uses Python's AST (Abstract Syntax Tree) to analyze code. No regex nonsense here.

1. Parse Python files with `libcst` - the right way
2. Walk the AST looking for patterns - precise and unforgiving
3. Flag violations with file, line, and message - so you know exactly what broke
4. Suggest fixes - because we're not here to ruin your day, just your mistakes

This approach is:

- **Fast**: Analyzes thousands of files in seconds. Even your disaster codebase.
- **Accurate**: AST-based analysis means zero false positives. We're not guessing.
- **Safe**: Read-only. We find problems, we don't break your code.

## Policy Configuration

Customize each policy in `loly.yml` to match your risk tolerance:

```yaml
exception_exc_info:
  levels: [error]        # Only check error logs (recommended)
  severity: fail         # Block CI. No mercy.

log_loop:
  levels: [info, debug]  # Check info and debug logs
  severity: warn         # Warn but don't block (easing in? Fair enough.)
```

## Severity Levels

**`fail`**: Exit code 1, blocks CI. This is the serious setting.

**`warn`**: Print a warning, exit code 0. The "I'll fix it later" setting. (You won't.)

**`info`**: Just informational. Perfect if you like living dangerously.

---

## Ready to Learn?

- [LY001: Exception exc_info](ly001-exception-exc-info.md) - The missing stack trace that will haunt you
- [LY002: Log Loop](ly002-log-loop.md) - The performance disaster hiding in plain sight

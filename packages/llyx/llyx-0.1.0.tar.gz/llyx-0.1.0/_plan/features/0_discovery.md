# Feature - Eligible File(s) Discovery

Active: True

policy: not a policy but a feature of the tool

What it does: Finds all logging calls regardless of how the logger is named.

Examples:
```py
logging.error("msg")           # ✓ Standard library
logger.error("msg")            # ✓ Common pattern
self.logger.error("msg")       # ✓ Class attribute
log.error("msg")               # ✓ Alternative name
my_custom_logger.error("msg")  # ✓ If configured in yaml
```

Configuration:
```yaml
yamlloggers:
  names: ["logging", "logger", "log", "self.logger"]
```
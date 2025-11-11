# Contributing

We welcome contributions! Bug fixes, new policies, documentation—all appreciated.

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/loly.git
cd loly
uv sync
uv run pytest
```

**Requirements:** Python 3.9+, [uv](https://docs.astral.sh/uv/), or pip

## Adding a Policy

### 1. Create the Policy

Create `src/loly/policies/your_policy.py`:

```python
from pathlib import Path
from typing import List, Dict
import libcst as cst
from loly.policies.base import BasePolicy


class _YourPolicyVisitor(cst.CSTVisitor):
    def __init__(self, levels: List[str], logger_names: List[str],
                 file_path: Path, wrapper: cst.MetadataWrapper):
        self.levels = levels
        self.logger_names = logger_names
        self.file_path = file_path
        self.violations = []
        self._wrapper = wrapper

    def visit_Call(self, node: cst.Call) -> None:
        if self._should_flag(node):
            self.violations.append({
                "file": str(self.file_path),
                "line": self._get_line_number(node),
                "code": "LY00X",
                "message": "Violation message",
                "category": "your_policy",
                "severity": "fail"
            })

    def _get_line_number(self, node: cst.CSTNode) -> int:
        try:
            pos = self._wrapper.resolve(cst.metadata.PositionProvider)[node]
            return pos.start.line
        except:
            return 0


class YourPolicy(BasePolicy):
    @classmethod
    def check(cls, code: str, file_path: Path, levels: List[str],
              logger_names: List[str]) -> List[Dict]:
        module = cst.parse_module(code)
        wrapper = cst.MetadataWrapper(module)
        visitor = _YourPolicyVisitor(levels, logger_names, file_path, wrapper)
        wrapper.visit(visitor)
        return visitor.violations
```

### 2. Write Tests

Create `tests/unit/src/loly/policies/test_your_policy.py`:

```python
from pathlib import Path
from loly.policies.your_policy import YourPolicy


def test_pass():
    code = """logger.info("valid pattern")"""
    violations = YourPolicy.check(code, Path("test.py"), ["info"], ["logger"])
    assert len(violations) == 0


def test_fail():
    code = """logger.info("invalid pattern")"""
    violations = YourPolicy.check(code, Path("test.py"), ["info"], ["logger"])
    assert len(violations) == 1
    assert violations[0]["code"] == "LY00X"
```

### 3. Register the Policy

Add to `src/loly/linter.py`:

```python
from loly.policies.your_policy import YourPolicy

POLICIES = {
    "exception_exc_info": ExceptionExcInfoPolicy,
    "log_loop": LogLoopPolicy,
    "your_policy": YourPolicy,
}
```

### 4. Document the Policy

Create `docs_site/docs/policies/ly00x-your-policy.md`. Follow the format of existing policies (Problem → Solution → Benefits → Examples).

## Code of Conduct

Be respectful and constructive. Trolling is not welcome.

---

Questions? Open an issue or reach out. We're here to help.

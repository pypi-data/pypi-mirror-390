from pathlib import Path
from typing import List, Dict
import pytest
from loly.policies.base import BasePolicy
from loly.policies.exception_exc_info import ExceptionExcInfoPolicy
from loly.policies.log_loop import LogLoopPolicy


def test_base_policy_is_abstract():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BasePolicy()


def test_policy_must_implement_check():
    class IncompletePolicy(BasePolicy):
        pass

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IncompletePolicy()


def test_exception_exc_info_inherits_from_base():
    assert issubclass(ExceptionExcInfoPolicy, BasePolicy)


def test_log_loop_inherits_from_base():
    assert issubclass(LogLoopPolicy, BasePolicy)


def test_policy_check_returns_correct_format():
    code = """
try:
    connect()
except Exception:
    logger.error("Failed")
"""
    violations = ExceptionExcInfoPolicy.check(
        code, Path("test.py"), ["error"], ["logger"]
    )

    assert isinstance(violations, list)
    assert len(violations) == 1

    violation = violations[0]
    assert "file" in violation
    assert "line" in violation
    assert "message" in violation
    assert isinstance(violation["file"], str)
    assert isinstance(violation["line"], int)
    assert isinstance(violation["message"], str)


def test_concrete_policy_with_check_implementation():
    """A complete policy implementation works correctly."""

    class ValidPolicy(BasePolicy):
        @classmethod
        def check(
            cls, code: str, file_path: Path, levels: List[str], logger_names: List[str]
        ) -> List[Dict]:
            return [{"file": str(file_path), "line": 1, "message": "test"}]

    violations = ValidPolicy.check("", Path("test.py"), ["info"], ["logger"])
    assert len(violations) == 1
    assert violations[0]["message"] == "test"


def test_all_policies_have_consistent_interface():
    """All policy classes have the same check() signature."""
    policies = [ExceptionExcInfoPolicy, LogLoopPolicy]

    for policy in policies:
        assert hasattr(policy, "check")
        assert callable(policy.check)

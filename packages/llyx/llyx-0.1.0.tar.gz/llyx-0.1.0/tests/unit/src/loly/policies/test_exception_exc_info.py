from pathlib import Path
from loly.policies.exception_exc_info import ExceptionExcInfoPolicy


def test_policy_detects_missing_exc_info_in_except_block():
    code = """
try:
    connect_db()
except Exception:
    logger.error("Connection failed")
"""
    violations = ExceptionExcInfoPolicy.check(
        code, Path("test.py"), ["error"], ["logger"]
    )

    assert len(violations) == 1
    assert violations[0]["message"] == "Missing exc_info=True in exception handler"
    assert violations[0]["line"] == 5


def test_policy_passes_when_exc_info_is_true():
    code = """
try:
    connect_db()
except Exception:
    logger.error("Connection failed", exc_info=True)
"""
    violations = ExceptionExcInfoPolicy.check(
        code, Path("test.py"), ["error"], ["logger"]
    )

    assert len(violations) == 0


def test_policy_ignores_logging_outside_except_block():
    code = """
if error:
    logger.error("Something wrong")
"""
    violations = ExceptionExcInfoPolicy.check(
        code, Path("test.py"), ["error"], ["logger"]
    )

    assert len(violations) == 0


def test_policy_detects_multiple_logger_names():
    code = """
try:
    connect_db()
except Exception:
    logging.error("Failed")
"""
    violations = ExceptionExcInfoPolicy.check(
        code, Path("test.py"), ["error"], ["logger", "logging"]
    )

    assert len(violations) == 1


def test_policy_respects_log_levels():
    code = """
try:
    connect_db()
except Exception:
    logger.info("Connection failed")
"""
    violations = ExceptionExcInfoPolicy.check(
        code, Path("test.py"), ["error"], ["logger"]
    )

    assert len(violations) == 0


def test_policy_enforces_on_any_level():
    code = """
try:
    connect_db()
except Exception:
    logger.info("Connection failed")
"""
    violations = ExceptionExcInfoPolicy.check(
        code, Path("test.py"), ["any"], ["logger"]
    )

    assert len(violations) == 1


def test_policy_detects_exc_info_false():
    code = """
try:
    connect_db()
except Exception:
    logger.error("Connection failed", exc_info=False)
"""
    violations = ExceptionExcInfoPolicy.check(
        code, Path("test.py"), ["error"], ["logger"]
    )

    assert len(violations) == 1
    assert "exc_info=True" in violations[0]["message"]


def test_policy_handles_nested_try_except():
    code = """
try:
    try:
        connect_db()
    except ValueError:
        logger.error("Inner error")
except Exception:
    logger.error("Outer error", exc_info=True)
"""
    violations = ExceptionExcInfoPolicy.check(
        code, Path("test.py"), ["error"], ["logger"]
    )

    assert len(violations) == 1
    assert violations[0]["line"] == 6

from pathlib import Path
from loly.policies.consistent_kv import ConsistentKVPolicy


def test_static_string_no_variables_passes():
    """Static string with no variables: no validation needed."""
    code = '''logger.error("something went wrong key=value")'''
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 0


def test_percent_formatting_variable_without_key_fails():
    """% formatting with variable without key prefix: fails."""
    code = '''logger.error("something went wrong key:%s", status)'''
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 1
    assert violations[0]["code"] == "LY003"


def test_fstring_variable_with_debug_syntax_passes():
    """f-string with Python 3.8+ debug syntax {key=}: passes."""
    code = '''logger.error(f"something went wrong {key=}")'''
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 0


def test_static_string_with_different_delimiter_passes():
    """Static string with delimiter mismatch: not validated, so passes."""
    code = '''logger.error("something went wrong key:value")'''
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 0


def test_fstring_variable_with_correct_delimiter_passes():
    """f-string with variable and correct delimiter: passes."""
    code = '''logger.error(f"user_id={user_id} status={status}")'''
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 0


def test_fstring_variable_without_key_fails():
    """f-string with variable but no key prefix: fails."""
    code = '''logger.error(f"Error occurred {error}")'''
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 1
    assert violations[0]["code"] == "LY003"


def test_fstring_variable_with_wrong_delimiter_fails():
    """f-string with variable but wrong delimiter: fails."""
    code = '''logger.error(f"user_id:{user_id}")'''
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 1
    assert violations[0]["code"] == "LY003"


def test_percent_formatting_variable_with_key_passes():
    """% formatting with variable and correct key format: passes."""
    code = '''logger.error("user_id=%s", user_id)'''
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 0


def test_percent_string_with_escape_sequences():
    """% formatting with escape sequences in string literal: handles correctly."""
    code = r'''logger.error("status=%s\npath=%s", status, path)'''
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 0


def test_percent_string_raw_string():
    """% formatting with raw string literal: handles correctly."""
    code = r'''logger.error(r"path=%s\nbackslash=%s", path, backslash)'''
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 0


def test_percent_string_triple_quoted():
    """% formatting with triple-quoted string: handles correctly."""
    code = '''logger.error("""user_id=%s\nstatus=%s""", user_id, status)'''
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 0


def test_percent_string_single_quotes():
    """% formatting with single quotes: handles correctly."""
    code = """logger.error('user_id=%s', user_id)"""
    violations = ConsistentKVPolicy.check(
        code, Path("test.py"), ["error"], ["logger"], delimiter="="
    )
    assert len(violations) == 0

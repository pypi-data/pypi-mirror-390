from pathlib import Path
from loly.policies.log_loop import LogLoopPolicy


def test_detects_unconditional_logging_in_for_loop():
    code = """
for user in users:
    logger.info(f"Processing user {user.id}")
    process_user(user)
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["info"], ["logger"])

    assert len(violations) == 1
    assert "hot loop" in violations[0]["message"].lower()
    assert violations[0]["line"] == 3


def test_detects_unconditional_logging_in_while_loop():
    code = """
while not connected:
    logger.warning("Waiting for connection...")
    time.sleep(1)
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["warning"], ["logger"])

    assert len(violations) == 1
    assert violations[0]["line"] == 3


def test_detects_multiple_logs_in_same_loop():
    code = """
for item in items:
    logger.debug("Start processing")
    process(item)
    logger.debug("End processing")
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["debug"], ["logger"])

    assert len(violations) == 2
    assert violations[0]["line"] == 3
    assert violations[1]["line"] == 5


def test_detects_nested_loop_logging():
    code = """
for batch in batches:
    for record in batch:
        logger.debug(f"Processing record {record.id}")
        process_record(record)
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["debug"], ["logger"])

    assert len(violations) == 1
    assert violations[0]["line"] == 4


def test_passes_conditional_logging_with_modulo():
    code = """
for i, user in enumerate(users):
    if i % 100 == 0:
        logger.info(f"Progress: {i}/{len(users)}")
    process_user(user)
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["info"], ["logger"])

    assert len(violations) == 0


def test_passes_conditional_logging_with_data_check():
    code = """
for user in users:
    if user.is_premium:
        logger.info(f"Processing premium user {user.id}")
    process_user(user)
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["info"], ["logger"])

    assert len(violations) == 0


def test_passes_logging_in_exception_handler():
    code = """
for user in users:
    try:
        process_user(user)
    except Exception as e:
        logger.error(f"Failed to process user {user.id}", exc_info=True)
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["error"], ["logger"])

    assert len(violations) == 0


def test_passes_logging_outside_loop():
    code = """
logger.info(f"Processing {len(users)} users")
for user in users:
    process_user(user)
logger.info("Processing complete")
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["info"], ["logger"])

    assert len(violations) == 0


def test_respects_log_levels():
    code = """
for user in users:
    logger.debug(f"Processing user {user.id}")
    process_user(user)
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["info"], ["logger"])

    assert len(violations) == 0


def test_detects_with_any_level():
    code = """
for user in users:
    logger.debug(f"Processing user {user.id}")
    process_user(user)
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["any"], ["logger"])

    assert len(violations) == 1


def test_detects_multiple_logger_names():
    code = """
for item in items:
    logging.info("Processing item")
    process(item)
"""
    violations = LogLoopPolicy.check(
        code, Path("test.py"), ["info"], ["logger", "logging"]
    )

    assert len(violations) == 1


def test_passes_logging_in_nested_conditional():
    code = """
for user in users:
    if user.age > 18:
        if user.is_active:
            logger.info(f"Processing active adult {user.id}")
    process_user(user)
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["info"], ["logger"])

    assert len(violations) == 0


def test_detects_logging_in_loop_with_conditional_elsewhere():
    code = """
for user in users:
    logger.info(f"Processing user {user.id}")
    if user.is_premium:
        upgrade_user(user)
    process_user(user)
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["info"], ["logger"])

    assert len(violations) == 1
    assert violations[0]["line"] == 3


def test_passes_with_list_comprehension():
    code = """
results = [process(item) for item in items]
logger.info(f"Processed {len(results)} items")
"""
    violations = LogLoopPolicy.check(code, Path("test.py"), ["info"], ["logger"])

    assert len(violations) == 0

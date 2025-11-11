"""Test file with known violations."""

import logging

logger = logging.getLogger(__name__)


# LY001: Missing exc_info=True
def test_ly001():
    try:
        x = 1 / 0
    except Exception:
        logger.error("Division error")  # Should fail - missing exc_info=True


# LY002: Logging in loop
def test_ly002():
    items = [1, 2, 3, 4, 5]
    for item in items:
        logger.info(f"Processing {item}")  # Should fail - unconditional logging in loop

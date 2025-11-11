"""Sample file with exception_exc_info violations."""

import logging

logger = logging.getLogger(__name__)


def process_data(data):
    """Function with missing exc_info violations."""
    try:
        result = int(data)
        return result * 2
    except ValueError:
        # LY001: Missing exc_info=True
        logger.error("Failed to process data")
        return None


def process_batch(items):
    """Function with proper exc_info usage."""
    results = []
    for item in items:
        try:
            results.append(int(item))
        except ValueError:
            # This one is correct
            logger.error(f"Invalid item: {item}", exc_info=True)
    return results


def validate_config(config):
    """Another missing exc_info violation."""
    try:
        required_keys = ["host", "port"]
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing key: {key}")
    except KeyError:
        # LY001: Missing exc_info=True
        logger.error("Configuration validation failed")
        return False
    return True

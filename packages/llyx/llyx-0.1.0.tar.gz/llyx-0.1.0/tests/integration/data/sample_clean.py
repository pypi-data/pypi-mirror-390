"""Sample file with no violations - should pass all checks."""

import logging

logger = logging.getLogger(__name__)


def process_safely(data):
    """Function with proper exc_info usage."""
    try:
        result = int(data)
        return result * 2
    except ValueError:
        logger.error("Failed to process data", exc_info=True)
        return None


def batch_process(items):
    """Function with logging outside loop - no violations."""
    logger.info(f"Starting batch processing of {len(items)} items")

    results = []
    for item in items:
        results.append(process_item(item))

    logger.info("Batch processing complete")
    return results


def process_item(item):
    """Helper function."""
    return item * 2

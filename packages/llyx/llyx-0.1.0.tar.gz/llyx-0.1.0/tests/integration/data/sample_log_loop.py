"""Sample file with log_loop violations."""

import logging

logger = logging.getLogger(__name__)


def process_users_bad(users):
    """Function with unconditional logging in loop - LY002."""
    for user in users:
        logger.info(f"Processing user {user['id']}")
        process_user(user)


def process_users_good(users):
    """Function with conditional logging - should pass."""
    for i, user in enumerate(users):
        if i % 100 == 0:
            logger.info(f"Progress: {i}/{len(users)}")
        process_user(user)


def sync_items_bad(items):
    """Another log_loop violation - LY002."""
    for item in items:
        logger.debug(f"Syncing item {item}")
        sync_item(item)


def process_user(user):
    """Helper function."""
    pass


def sync_item(item):
    """Helper function."""
    pass
